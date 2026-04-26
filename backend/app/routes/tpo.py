"""
ResumX V2 – TPO (Placement Cell) Routes
=========================================
GET  /api/tpo/report              – get latest batch readiness report
POST /api/tpo/report/generate     – trigger InstitutionalAnalyst for fresh report
GET  /api/tpo/export/json         – export batch skill-gap data as JSON
GET  /api/tpo/export/csv          – export batch skill-gap data as CSV
GET  /api/tpo/students            – list all students in the org with their metrics
GET  /api/tpo/stats/<org_id>      – analytics counter + recent activity
GET  /api/tpo/heatmap             – batch skill frequency heatmap data
GET  /api/tpo/readiness           – placement readiness score + actionable insight
POST /api/tpo/export/recruiter    – match resumes to a JD and download ZIP
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timedelta, timezone

from flask import Blueprint, Response, jsonify, request

from app.core.auth import require_auth
from app.db.models import AgentSession, AnalysisLog, Organization, TPOReport, User
from app.db.session import SessionLocal

tpo_bp = Blueprint("tpo", __name__, url_prefix="/api/tpo")


# ── Helper: build batch_records from DB ──────────────────────────────────────

def _load_batch_records(db, org_id: str) -> list:
    """
    Pull the latest completed AgentSession per student in the org.
    Returns a list of StudentBatchRecord-compatible dicts.
    """
    users = db.query(User).filter_by(org_id=org_id, is_active=True, role="student").all()
    records = []
    for user in users:
        session = (
            db.query(AgentSession)
            .filter_by(user_id=user.id)
            .order_by(AgentSession.updated_at.desc())
            .first()
        )
        if session:
            records.append({
                "user_id":          user.id,
                "full_name":        user.full_name or user.email,
                "match_pct":        session.match_pct or 0.0,
                "skill_gaps":       session.skill_gaps or [],
                "completed_agents": session.completed_agents or [],
            })
    return records


# ── GET /api/tpo/report ───────────────────────────────────────────────────────

@tpo_bp.route("/report", methods=["GET"])
@require_auth("tpo", "admin")
def get_report():
    db = SessionLocal()
    try:
        report = (
            db.query(TPOReport)
            .filter_by(org_id=request.org_id)
            .order_by(TPOReport.generated_at.desc())
            .first()
        )
        if not report:
            return jsonify({"message": "No report generated yet. POST /api/tpo/report/generate"}), 404

        return jsonify({
            "report_id":       report.id,
            "generated_at":    report.generated_at.isoformat(),
            "total_students":  report.total_students,
            "avg_match_pct":   report.avg_match_pct,
            "readiness_score": report.readiness_score,
            "top_skill_gaps":  report.top_skill_gaps,
            "report_data":     report.report_data,
        })
    finally:
        db.close()


# ── POST /api/tpo/report/generate ────────────────────────────────────────────

@tpo_bp.route("/report/generate", methods=["POST"])
@require_auth("tpo", "admin")
def generate_report():
    db = SessionLocal()
    try:
        org = db.query(Organization).filter_by(id=request.org_id, is_active=True).first()
        if not org:
            return jsonify({"error": "Organisation not found"}), 404

        batch_records = _load_batch_records(db, request.org_id)
        if not batch_records:
            return jsonify({"error": "No student data available yet"}), 400

        # Run the InstitutionalAnalyst node
        from app.agents.graph import run_tpo_report
        result = run_tpo_report(
            org_id=request.org_id,
            batch_records=batch_records,
            dream_companies=org.dream_companies or [],
        )

        report_data = result.get("batch_report", {})
        raw_agg     = report_data.pop("_raw_aggregation", {})

        # Persist to DB
        tpo_report = TPOReport(
            org_id=request.org_id,
            report_data=report_data,
            total_students=raw_agg.get("total_students", len(batch_records)),
            avg_match_pct=raw_agg.get("avg_match_pct"),
            top_skill_gaps=raw_agg.get("top_skill_gaps", []),
            readiness_score=report_data.get("batch_readiness_score"),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db.add(tpo_report)
        db.commit()
        db.refresh(tpo_report)

        return jsonify({
            "report_id":       tpo_report.id,
            "readiness_score": tpo_report.readiness_score,
            "total_students":  tpo_report.total_students,
            "report_data":     report_data,
        }), 201
    finally:
        db.close()


# ── GET /api/tpo/export/json ──────────────────────────────────────────────────

@tpo_bp.route("/export/json", methods=["GET"])
@require_auth("tpo", "admin")
def export_json():
    db = SessionLocal()
    try:
        records = _load_batch_records(db, request.org_id)
        payload = json.dumps(records, indent=2)
        return Response(
            payload,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=batch_skill_gaps.json"},
        )
    finally:
        db.close()


# ── GET /api/tpo/export/csv ───────────────────────────────────────────────────

@tpo_bp.route("/export/csv", methods=["GET"])
@require_auth("tpo", "admin")
def export_csv():
    db = SessionLocal()
    try:
        records = _load_batch_records(db, request.org_id)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["student_id", "full_name", "match_pct",
                         "skill_gaps", "completed_agents"])
        for r in records:
            writer.writerow([
                r["user_id"],
                r["full_name"],
                r["match_pct"],
                "; ".join(
                    g if isinstance(g, str) else g.get("skill", "")
                    for g in r["skill_gaps"]
                ),
                "; ".join(r["completed_agents"]),
            ])

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=batch_skill_gaps.csv"},
        )
    finally:
        db.close()


# ── GET /api/tpo/students ─────────────────────────────────────────────────────

@tpo_bp.route("/students", methods=["GET"])
@require_auth("tpo", "admin")
def list_students():
    db = SessionLocal()
    try:
        records = _load_batch_records(db, request.org_id)
        return jsonify({"students": records, "total": len(records)})
    finally:
        db.close()


# ── GET /api/v1/tpo/stats/<org_id> ───────────────────────────────────────────

@tpo_bp.route("/stats/<org_id>", methods=["GET"])
@require_auth("tpo", "admin")
def get_stats(org_id: str):
    """
    Returns analytics for the TPO Dashboard StatCard.

    Response:
      {
        "total_count":     <int>,
        "recent_activity": [ { student_name, timestamp, match_score, model_used }, ... ],
        "daily_stats":     { "last_24h": <int> }
      }

    Access control: TPO/admin can only query their own org_id.
    """
    # Enforce tenant isolation – TPOs can only see their own org
    if request.org_id != org_id and request.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    db = SessionLocal()
    try:
        from app.services.analytics_service import get_tpo_stats
        stats = get_tpo_stats(db, org_id)
        return jsonify(stats)
    finally:
        db.close()


# ── GET /api/tpo/heatmap ──────────────────────────────────────────────────────

@tpo_bp.route("/heatmap", methods=["GET"])
@require_auth("tpo", "admin")
def get_heatmap():
    """
    Returns skill frequency data for the batch heatmap visualization.

    Response:
      {
        "top_matching_skills": [{"skill": "Python", "count": 45, "pct": 90}, ...],
        "top_missing_skills":  [{"skill": "Docker", "count": 38, "pct": 76}, ...],
        "total_students": 50
      }
    """
    db = SessionLocal()
    try:
        from app.services.analytics_engine import compute_skill_heatmap
        data = compute_skill_heatmap(db, request.org_id)
        return jsonify(data)
    finally:
        db.close()


# ── GET /api/tpo/readiness ────────────────────────────────────────────────────

@tpo_bp.route("/readiness", methods=["GET"])
@require_auth("tpo", "admin")
def get_readiness():
    """
    Returns the Placement Readiness Score and actionable insight.

    Response:
      {
        "readiness_score": 87.5,
        "avg_ats_match": 82.0,
        "project_completeness": 95.0,
        "interview_participation": 100.0,
        "insight": "Based on this score, your batch is a strong match..."
      }
    """
    db = SessionLocal()
    try:
        from app.services.analytics_engine import (
            compute_readiness_score,
            compute_skill_heatmap,
            generate_actionable_insight,
        )

        scores = compute_readiness_score(db, request.org_id)
        heatmap = compute_skill_heatmap(db, request.org_id)

        org = db.query(Organization).filter_by(id=request.org_id).first()
        dream_companies = (org.dream_companies or []) if org else []

        insight = generate_actionable_insight(
            scores["readiness_score"],
            heatmap.get("top_missing_skills", []),
            dream_companies,
        )

        return jsonify({**scores, "insight": insight})
    finally:
        db.close()


# ── POST /api/tpo/export/recruiter ────────────────────────────────────────────

@tpo_bp.route("/export/recruiter", methods=["POST"])
@require_auth("tpo", "admin")
def recruiter_export():
    """
    Matches all org resumes against a pasted JD and returns a ZIP of the top 50.

    Body: { "job_description": "...", "top_n": 50 }

    The export event is logged to AnalysisLogs for privacy auditing.
    """
    data = request.get_json() or {}
    jd = (data.get("job_description") or "").strip()
    if not jd:
        return jsonify({"error": "job_description is required"}), 400

    top_n = min(int(data.get("top_n", 50)), 100)  # cap at 100

    db = SessionLocal()
    try:
        from app.services.export_service import build_resume_zip
        zip_bytes, manifest = build_resume_zip(
            db,
            org_id=request.org_id,
            job_description=jd,
            requested_by_user_id=request.user_id,
            top_n=top_n,
        )

        if not manifest:
            return jsonify({"error": "No student resumes found in this organisation"}), 404

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"top_{len(manifest)}_matches_{timestamp}.zip"

        return Response(
            zip_bytes,
            mimetype="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    finally:
        db.close()
