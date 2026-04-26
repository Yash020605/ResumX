"""
ResumX V2 – TPO Session Service
================================
Business logic for live session management.

Provides:
  - generate_session_code(db, org_id) → str
  - create_session(db, org_id, created_by_user_id) → TPOLiveSession
  - join_session(db, session_code, student_id, student_org_id) → (SessionParticipant, bool)
  - end_session(db, session_id, requesting_org_id) → TPOLiveSession
  - get_dashboard(db, session_id, requesting_org_id) → dict
  - get_summary(db, session_id, requesting_org_id) → dict
  - list_sessions(db, org_id, status, page, per_page) → dict
"""
from __future__ import annotations

import math
import random
import string
from datetime import datetime, timezone

from sqlalchemy import func

from app.db.models import (
    AnalysisLog,
    Organization,
    SessionParticipant,
    TPOLiveSession,
    User,
)


# ── Custom Exceptions ─────────────────────────────────────────────────────────

class SessionNotFoundError(Exception):
    """Raised when a session cannot be found (404-equivalent)."""
    pass


class SessionConflictError(Exception):
    """Raised on duplicate active session or re-ending an ended session (409-equivalent)."""
    pass


class SessionForbiddenError(Exception):
    """Raised when the requesting org does not own the session (403-equivalent)."""
    pass


class SessionEndedError(Exception):
    """Raised when a student tries to join a session that has already ended (410-equivalent)."""
    pass


# ── Constants ─────────────────────────────────────────────────────────────────

_CHARSET = string.ascii_uppercase + string.digits  # A-Z + 0-9 (36 chars)
_MAX_CODE_RETRIES = 10
_MAX_PER_PAGE = 20


# ── Helpers ───────────────────────────────────────────────────────────────────

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _get_session_or_404(db, session_id: str) -> TPOLiveSession:
    """Fetch a TPOLiveSession by id; raise SessionNotFoundError if missing."""
    session = db.query(TPOLiveSession).filter(TPOLiveSession.id == session_id).first()
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    return session


def _check_org_ownership(session: TPOLiveSession, requesting_org_id: str) -> None:
    """Raise SessionForbiddenError if the session does not belong to requesting_org_id."""
    if session.org_id != requesting_org_id:
        raise SessionForbiddenError(
            f"Session '{session.id}' does not belong to organisation '{requesting_org_id}'."
        )


# ── Task 2.1 — generate_session_code ─────────────────────────────────────────

def generate_session_code(db, org_id: str) -> str:
    """
    Generate a unique session code for the given organisation.

    Format: {ORG_PREFIX}-{YEAR}-{XX}
    Example: ADYPU-2025-A1

    - ORG_PREFIX: first word of Organization.name, uppercased, max 6 chars
    - YEAR: current UTC year (4 digits)
    - XX: 2 random characters from A-Z + 0-9

    Uniqueness is checked against active sessions only (status="active").
    Retries up to 10 times; raises RuntimeError on exhaustion.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org and org.name:
        prefix = (org.name.split()[0].upper())[:6]
    else:
        prefix = "ORG"

    year = _utcnow().year

    for _ in range(_MAX_CODE_RETRIES):
        suffix = "".join(random.choices(_CHARSET, k=2))
        code = f"{prefix}-{year}-{suffix}"
        exists = (
            db.query(TPOLiveSession)
            .filter(TPOLiveSession.session_code == code, TPOLiveSession.status == "active")
            .first()
        )
        if not exists:
            return code

    raise RuntimeError(
        f"Could not generate a unique session code for org '{org_id}' after "
        f"{_MAX_CODE_RETRIES} attempts."
    )


# ── Task 2.3 — create_session ─────────────────────────────────────────────────

def create_session(db, org_id: str, created_by_user_id: str) -> TPOLiveSession:
    """
    Create a new active session for the given organisation.

    Raises:
        SessionConflictError: if an active session already exists for this org (409).
    """
    existing = (
        db.query(TPOLiveSession)
        .filter(TPOLiveSession.org_id == org_id, TPOLiveSession.status == "active")
        .first()
    )
    if existing:
        err = SessionConflictError(
            f"An active session already exists for organisation '{org_id}'."
        )
        err.existing_session_id = existing.id  # type: ignore[attr-defined]
        raise err

    code = generate_session_code(db, org_id)

    session = TPOLiveSession(
        org_id=org_id,
        created_by_user_id=created_by_user_id,
        session_code=code,
        status="active",
        started_at=_utcnow(),
        participant_count=0,
        analyses_completed=0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# ── Task 2.6 — join_session ───────────────────────────────────────────────────

def join_session(
    db,
    session_code: str,
    student_id: str,
    student_org_id: str,
) -> tuple[SessionParticipant, bool]:
    """
    Join a session by session code.

    Returns:
        (participant, already_joined)
        already_joined=True  → student was already a participant (idempotent)
        already_joined=False → new participant record created

    Raises:
        SessionNotFoundError:  no session with that code exists (404).
        SessionEndedError:     session exists but has status="ended" (410).
        SessionForbiddenError: session.org_id != student_org_id (403).
    """
    session = (
        db.query(TPOLiveSession)
        .filter(TPOLiveSession.session_code == session_code)
        .first()
    )
    if not session:
        raise SessionNotFoundError(f"No session found with code '{session_code}'.")

    if session.status == "ended":
        raise SessionEndedError(
            f"Session '{session_code}' has ended and is no longer accepting participants."
        )

    if session.org_id != student_org_id:
        raise SessionForbiddenError(
            f"Session '{session_code}' does not belong to your organisation."
        )

    # Check for existing participation (idempotent join)
    existing_participant = (
        db.query(SessionParticipant)
        .filter(
            SessionParticipant.session_id == session.id,
            SessionParticipant.student_id == student_id,
        )
        .first()
    )
    if existing_participant:
        return existing_participant, True

    # Create new participant record
    participant = SessionParticipant(
        session_id=session.id,
        student_id=student_id,
        joined_at=_utcnow(),
        analyses_completed=0,
    )
    db.add(participant)

    # Increment participant count on the session
    session.participant_count = (session.participant_count or 0) + 1

    db.commit()
    db.refresh(participant)
    return participant, False


# ── Task 2.10 — end_session ───────────────────────────────────────────────────

def end_session(db, session_id: str, requesting_org_id: str) -> TPOLiveSession:
    """
    End an active session.

    Raises:
        SessionNotFoundError:  session not found (404).
        SessionForbiddenError: org mismatch (403).
        SessionConflictError:  session already ended (409).
    """
    session = _get_session_or_404(db, session_id)
    _check_org_ownership(session, requesting_org_id)

    if session.status == "ended":
        raise SessionConflictError("Session has already ended.")

    session.status = "ended"
    session.ended_at = _utcnow()

    db.commit()
    db.refresh(session)
    return session


# ── Task 2.12 — get_dashboard ─────────────────────────────────────────────────

def get_dashboard(db, session_id: str, requesting_org_id: str) -> dict:
    """
    Return live dashboard data for a session.

    Raises:
        SessionNotFoundError:  session not found (404).
        SessionForbiddenError: org mismatch (403).
    """
    session = _get_session_or_404(db, session_id)
    _check_org_ownership(session, requesting_org_id)

    # Fetch all participants joined with their User record
    rows = (
        db.query(SessionParticipant, User)
        .join(User, User.id == SessionParticipant.student_id)
        .filter(SessionParticipant.session_id == session_id)
        .all()
    )

    participants = [
        {
            "student_id": p.student_id,
            "full_name": user.full_name or user.email,
            "email": user.email,
            "joined_at": p.joined_at.isoformat(),
            "analyses_completed": p.analyses_completed,
        }
        for p, user in rows
    ]

    return {
        "session_id": session.id,
        "session_code": session.session_code,
        "status": session.status,
        "started_at": session.started_at.isoformat(),
        "participant_count": session.participant_count,
        "analyses_completed": session.analyses_completed,
        "participants": participants,
    }


# ── Task 2.14 — get_summary ───────────────────────────────────────────────────

def get_summary(db, session_id: str, requesting_org_id: str) -> dict:
    """
    Return a post-session (or mid-session) summary with analysis statistics.

    Raises:
        SessionNotFoundError:  session not found (404).
        SessionForbiddenError: org mismatch (403).
    """
    session = _get_session_or_404(db, session_id)
    _check_org_ownership(session, requesting_org_id)

    now = _utcnow()
    ended_at = session.ended_at
    started_at = session.started_at

    # Normalise to aware datetimes (SQLite returns naive UTC datetimes)
    def _ensure_aware(dt: datetime) -> datetime:
        if dt is not None and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    started_at = _ensure_aware(started_at)
    ended_at = _ensure_aware(ended_at)

    # Duration in minutes (rounded to 1 decimal)
    reference_end = ended_at if ended_at else now
    duration_seconds = (reference_end - started_at).total_seconds()
    duration_minutes = round(duration_seconds / 60, 1)

    # Fetch all participants with their User records
    rows = (
        db.query(SessionParticipant, User)
        .join(User, User.id == SessionParticipant.student_id)
        .filter(SessionParticipant.session_id == session_id)
        .all()
    )

    participant_ids = [p.student_id for p, _ in rows]

    # Overall avg_match_score from AnalysisLog
    avg_score: float | None = None
    if participant_ids:
        q = db.query(func.avg(AnalysisLog.match_score)).filter(
            AnalysisLog.student_id.in_(participant_ids),
            AnalysisLog.timestamp >= started_at,
        )
        if ended_at:
            q = q.filter(AnalysisLog.timestamp <= ended_at)
        avg_score = q.scalar()
        if avg_score is not None:
            avg_score = round(float(avg_score), 1)

    # Per-participant avg_match_score
    per_student_avg: dict[str, float | None] = {}
    if participant_ids:
        per_q = (
            db.query(
                AnalysisLog.student_id,
                func.avg(AnalysisLog.match_score).label("avg_score"),
            )
            .filter(
                AnalysisLog.student_id.in_(participant_ids),
                AnalysisLog.timestamp >= started_at,
            )
        )
        if ended_at:
            per_q = per_q.filter(AnalysisLog.timestamp <= ended_at)
        per_q = per_q.group_by(AnalysisLog.student_id)
        for sid, avg in per_q.all():
            per_student_avg[sid] = round(float(avg), 1) if avg is not None else None

    participants = [
        {
            "student_id": p.student_id,
            "full_name": user.full_name or user.email,
            "email": user.email,
            "joined_at": p.joined_at.isoformat(),
            "analyses_completed": p.analyses_completed,
            "avg_match_score": per_student_avg.get(p.student_id),
        }
        for p, user in rows
    ]

    return {
        "session_id": session.id,
        "session_code": session.session_code,
        "status": session.status,
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat() if ended_at else None,
        "duration_minutes": duration_minutes,
        "participant_count": session.participant_count,
        "analyses_completed": session.analyses_completed,
        "avg_match_score": avg_score,
        "participants": participants,
    }


# ── Task 2.16 — list_sessions ─────────────────────────────────────────────────

def list_sessions(
    db,
    org_id: str,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """
    Return a paginated list of sessions for the given organisation.

    Args:
        db:       SQLAlchemy session.
        org_id:   Organisation to filter by.
        status:   Optional status filter ("active" | "ended").
        page:     1-based page number.
        per_page: Results per page (capped at 20).

    Returns:
        {
            "sessions": [...],
            "total": int,
            "page": int,
            "per_page": int,
            "pages": int,
        }
    """
    per_page = min(per_page, _MAX_PER_PAGE)
    page = max(page, 1)

    q = db.query(TPOLiveSession).filter(TPOLiveSession.org_id == org_id)

    if status is not None:
        q = q.filter(TPOLiveSession.status == status)

    total = q.count()

    sessions_rows = (
        q.order_by(TPOLiveSession.started_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    pages = math.ceil(total / per_page) if total > 0 else 1

    sessions = [
        {
            "session_id": s.id,
            "session_code": s.session_code,
            "status": s.status,
            "started_at": s.started_at.isoformat(),
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            "participant_count": s.participant_count,
            "analyses_completed": s.analyses_completed,
        }
        for s in sessions_rows
    ]

    return {
        "sessions": sessions,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }
