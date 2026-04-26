"""
ResumX V2 – TPO Live Session Routes
=====================================
POST /api/tpo/sessions                        – create a new live session
POST /api/tpo/sessions/<session_id>/end       – end an active session
GET  /api/tpo/sessions/<session_id>/dashboard – live dashboard for a session
GET  /api/tpo/sessions/<session_id>/summary   – post-session summary
GET  /api/tpo/sessions                        – paginated list of sessions
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth import require_auth
from app.db.session import SessionLocal
from app.services import session_service
from app.services.session_service import (
    SessionConflictError,
    SessionForbiddenError,
    SessionNotFoundError,
    SessionEndedError,
)

tpo_sessions_bp = Blueprint("tpo_sessions", __name__, url_prefix="/api/tpo")


# ── POST /api/tpo/sessions ────────────────────────────────────────────────────

@tpo_sessions_bp.route("/sessions", methods=["POST"])
@require_auth("tpo", "admin")
def create_session():
    """Create a new live session for the requesting organisation."""
    db = SessionLocal()
    try:
        s = session_service.create_session(db, request.org_id, request.user_id)
        return jsonify({
            "session_id":  s.id,
            "session_code": s.session_code,
            "status":      s.status,
            "started_at":  s.started_at.isoformat(),
        }), 201
    except SessionConflictError as err:
        return jsonify({
            "error": "An active session already exists for your organisation",
            "existing_session_id": err.existing_session_id,
        }), 409
    except Exception:
        return jsonify({"error": "Service temporarily unavailable. Please try again."}), 503
    finally:
        db.close()


# ── POST /api/tpo/sessions/<session_id>/end ───────────────────────────────────

@tpo_sessions_bp.route("/sessions/<session_id>/end", methods=["POST"])
@require_auth("tpo", "admin")
def end_session(session_id: str):
    """End an active session."""
    db = SessionLocal()
    try:
        s = session_service.end_session(db, session_id, request.org_id)
        duration_minutes = round(
            (s.ended_at - s.started_at).total_seconds() / 60, 1
        )
        return jsonify({
            "session_id":       s.id,
            "status":           s.status,
            "ended_at":         s.ended_at.isoformat(),
            "duration_minutes": duration_minutes,
        }), 200
    except SessionNotFoundError:
        return jsonify({"error": "Session not found"}), 404
    except SessionForbiddenError:
        return jsonify({"error": "You do not have permission to end this session"}), 403
    except SessionConflictError:
        return jsonify({"error": "Session has already ended"}), 409
    except Exception:
        return jsonify({"error": "Service temporarily unavailable. Please try again."}), 503
    finally:
        db.close()


# ── GET /api/tpo/sessions/<session_id>/dashboard ─────────────────────────────

@tpo_sessions_bp.route("/sessions/<session_id>/dashboard", methods=["GET"])
@require_auth("tpo", "admin")
def get_dashboard(session_id: str):
    """Return live dashboard data for a session."""
    db = SessionLocal()
    try:
        data = session_service.get_dashboard(db, session_id, request.org_id)
        return jsonify(data), 200
    except SessionNotFoundError:
        return jsonify({"error": "Session not found"}), 404
    except SessionForbiddenError:
        return jsonify({"error": "You do not have permission to view this session"}), 403
    except Exception:
        return jsonify({"error": "Service temporarily unavailable. Please try again."}), 503
    finally:
        db.close()


# ── GET /api/tpo/sessions/<session_id>/summary ───────────────────────────────

@tpo_sessions_bp.route("/sessions/<session_id>/summary", methods=["GET"])
@require_auth("tpo", "admin")
def get_summary(session_id: str):
    """Return a post-session summary with analysis statistics."""
    db = SessionLocal()
    try:
        data = session_service.get_summary(db, session_id, request.org_id)
        return jsonify(data), 200
    except SessionNotFoundError:
        return jsonify({"error": "Session not found"}), 404
    except SessionForbiddenError:
        return jsonify({"error": "You do not have permission to view this session"}), 403
    except Exception:
        return jsonify({"error": "Service temporarily unavailable. Please try again."}), 503
    finally:
        db.close()


# ── GET /api/tpo/sessions ─────────────────────────────────────────────────────

@tpo_sessions_bp.route("/sessions", methods=["GET"])
@require_auth("tpo", "admin")
def list_sessions():
    """Return a paginated list of sessions for the requesting organisation."""
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1

    try:
        per_page = min(int(request.args.get("per_page", 20)), 20)
    except (TypeError, ValueError):
        per_page = 20

    status = request.args.get("status") or None

    db = SessionLocal()
    try:
        data = session_service.list_sessions(
            db, request.org_id, status=status, page=page, per_page=per_page
        )
        return jsonify(data), 200
    except Exception:
        return jsonify({"error": "Service temporarily unavailable. Please try again."}), 503
    finally:
        db.close()
