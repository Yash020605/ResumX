"""
ResumX V2 – Session Persistence Routes
========================================
GET  /api/sessions/latest   – get user's latest active session state
POST /api/sessions/save     – save/update AgentState after a node transition
POST /api/sessions/resume   – resume a session and continue the graph
POST /api/sessions/join     – student joins a live TPO session by code
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.auth import require_auth
from app.db.models import AgentSession
from app.db.session import SessionLocal
from app.services import session_service
from app.services.session_service import (
    SessionNotFoundError, SessionForbiddenError, SessionEndedError
)

sessions_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")


@sessions_bp.route("/latest", methods=["GET"])
@require_auth("student", "tpo", "admin")
def get_latest():
    db = SessionLocal()
    try:
        session = (
            db.query(AgentSession)
            .filter_by(user_id=request.user_id, status="active")
            .order_by(AgentSession.updated_at.desc())
            .first()
        )
        if not session:
            return jsonify({"session": None, "message": "No active session found"}), 200

        return jsonify({
            "session_id":        session.id,
            "last_node":         session.last_node,
            "match_pct":         session.match_pct,
            "skill_gaps":        session.skill_gaps,
            "completed_agents":  session.completed_agents,
            "agent_state":       session.agent_state,
            "updated_at":        session.updated_at.isoformat(),
        })
    finally:
        db.close()


@sessions_bp.route("/save", methods=["POST"])
@require_auth("student", "tpo", "admin")
def save_session():
    """
    Called by the graph runner after every node transition to persist state.
    Body: { "session_id": "...", "agent_state": {...}, "last_node": "..." }
    """
    data       = request.get_json() or {}
    session_id = data.get("session_id")
    state      = data.get("agent_state", {})
    last_node  = data.get("last_node", "")

    db = SessionLocal()
    try:
        if session_id:
            session = db.query(AgentSession).filter_by(
                id=session_id, user_id=request.user_id
            ).first()
        else:
            session = None

        if session:
            session.agent_state      = state
            session.last_node        = last_node
            session.match_pct        = state.get("match_percentage")
            session.skill_gaps       = state.get("skill_gaps", [])
            session.completed_agents = state.get("completed_agents", [])
            if last_node == "END":
                session.status = "completed"
        else:
            session = AgentSession(
                user_id=request.user_id,
                org_id=request.org_id,
                agent_state=state,
                last_node=last_node,
                match_pct=state.get("match_percentage"),
                skill_gaps=state.get("skill_gaps", []),
                completed_agents=state.get("completed_agents", []),
                status="active",
            )
            db.add(session)

        db.commit()
        db.refresh(session)
        return jsonify({"session_id": session.id, "status": session.status})
    finally:
        db.close()


@sessions_bp.route("/resume", methods=["POST"])
@require_auth("student", "tpo", "admin")
def resume_session():
    """
    Resume a persisted session and continue the LangGraph pipeline.
    Body: { "session_id": "...", "message": "optional user message" }
    """
    data       = request.get_json() or {}
    session_id = data.get("session_id")
    user_msg   = data.get("message", "")

    db = SessionLocal()
    try:
        session = db.query(AgentSession).filter_by(
            id=session_id, user_id=request.user_id
        ).first()
        if not session:
            return jsonify({"error": "Session not found"}), 404

        from app.agents.graph import resume_session as graph_resume
        result = graph_resume(
            session_id=session_id,
            persisted_state=session.agent_state,
            new_user_message=user_msg,
        )

        # Persist updated state
        session.agent_state      = dict(result)
        session.last_node        = (result.get("completed_agents") or [""])[-1]
        session.match_pct        = result.get("match_percentage")
        session.skill_gaps       = result.get("skill_gaps", [])
        session.completed_agents = result.get("completed_agents", [])
        db.commit()

        return jsonify({
            "session_id":       session_id,
            "completed_agents": result.get("completed_agents", []),
            "match_percentage": result.get("match_percentage"),
            "last_node":        session.last_node,
        })
    finally:
        db.close()


@sessions_bp.route("/join", methods=["POST"])
@require_auth("student")
def join_session():
    """
    Student joins a live TPO session by session code.
    Body: { "session_code": "ADYPU-2025-A1" }
    """
    data = request.get_json() or {}
    session_code = data.get("session_code", "").strip()

    if not session_code:
        return jsonify({"error": "session_code is required"}), 400

    db = SessionLocal()
    try:
        participant, already_joined = session_service.join_session(
            db, session_code, request.user_id, request.org_id
        )
        return jsonify({
            "session_id":    participant.session_id,
            "session_code":  session_code,
            "joined_at":     participant.joined_at.isoformat(),
            "already_joined": already_joined,
        }), 200
    except SessionNotFoundError:
        return jsonify({"error": "No active session found with that code"}), 404
    except SessionForbiddenError:
        return jsonify({"error": "This session is not for your organisation"}), 403
    except SessionEndedError:
        return jsonify({"error": "This session has ended and is no longer accepting participants"}), 410
    except Exception:
        return jsonify({"error": "Service temporarily unavailable. Please try again."}), 503
    finally:
        db.close()
