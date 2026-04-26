"""
Analytics Service – Resume Counter & Audit Log
===============================================

Responsibilities:
  1. record_analysis()  – atomically increment org counter + insert AnalysisLog row
  2. get_tpo_stats()    – fetch total_count, recent_activity, daily_stats for dashboard

Concurrency safety:
  - Uses SQLAlchemy F() expression for the counter increment so concurrent
    transactions never overwrite each other (UPDATE orgs SET total = total + 1).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import AnalysisLog, Organization, User


def record_analysis(
    db: Session,
    *,
    org_id: str,
    student_id: Optional[str],
    model_used: str,
    match_score: Optional[float],
) -> AnalysisLog:
    """
    Called after a successful AnalyzerAgent run.

    1. Atomically increments Organization.total_resumes_analyzed.
    2. Inserts a new AnalysisLog row.
    3. Commits both in a single transaction.
    """
    from sqlalchemy import update
    from app.db.models import Base  # noqa – ensures mapper is loaded

    # Atomic increment – safe under concurrent load
    db.execute(
        update(Organization)
        .where(Organization.id == org_id)
        .values(total_resumes_analyzed=Organization.total_resumes_analyzed + 1)
        .execution_options(synchronize_session="fetch")
    )

    log = AnalysisLog(
        org_id=org_id,
        student_id=student_id,
        model_used=model_used,
        match_score=match_score,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_tpo_stats(db: Session, org_id: str) -> dict:
    """
    Returns the analytics payload for GET /api/v1/tpo/stats/{org_id}.

    Fields:
      total_count      – lifetime counter from Organization row
      recent_activity  – last 10 logs with student name, timestamp, match_score
      daily_stats      – count of analyses in the last 24 hours
    """
    # 1. Total counter
    org = db.query(Organization).filter_by(id=org_id).first()
    total_count = org.total_resumes_analyzed if org else 0

    # 2. Recent activity – last 10 logs
    recent_logs = (
        db.query(AnalysisLog)
        .filter(AnalysisLog.org_id == org_id)
        .order_by(AnalysisLog.timestamp.desc())
        .limit(10)
        .all()
    )

    recent_activity = []
    for log in recent_logs:
        student_name = "Anonymous"
        if log.student_id:
            user = db.query(User).filter_by(id=log.student_id).first()
            if user:
                student_name = user.full_name or user.email

        recent_activity.append({
            "student_name": student_name,
            "timestamp":    log.timestamp.isoformat(),
            "match_score":  log.match_score,
            "model_used":   log.model_used,
        })

    # 3. Daily stats – count in last 24 hours
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    daily_count = (
        db.query(func.count(AnalysisLog.id))
        .filter(AnalysisLog.org_id == org_id, AnalysisLog.timestamp >= cutoff)
        .scalar()
    ) or 0

    return {
        "total_count":     total_count,
        "recent_activity": recent_activity,
        "daily_stats":     {"last_24h": daily_count},
    }
