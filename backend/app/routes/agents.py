"""
ResumX V2 – LangGraph Agent Routes
====================================
POST /api/agents/run     – full or targeted pipeline (auth optional)
GET  /api/agents/status  – LangGraph availability check
"""
from flask import Blueprint, request, jsonify
from app.utils.validators import InputValidator
from app.core.auth import decode_token

agents_bp = Blueprint("agents", __name__, url_prefix="/api/agents")


def _get_identity():
    """
    Optionally extract user_id / org_id / dream_companies from JWT.
    Returns (None, None, []) for unauthenticated requests so the
    pipeline still works without login (backward-compatible).
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, None, []
    payload = decode_token(auth.split(" ", 1)[1])
    if not payload:
        return None, None, []

    user_id = payload.get("sub")
    org_id  = payload.get("org_id")

    # Load dream_companies from DB if org_id present
    dream_companies = []
    if org_id:
        try:
            from app.db.models import Organization
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                org = db.query(Organization).filter_by(id=org_id).first()
                dream_companies = (org.dream_companies or []) if org else []
            finally:
                db.close()
        except Exception:
            pass

    return user_id, org_id, dream_companies


@agents_bp.route("/run", methods=["POST"])
def run_agents():
    """
    Run the full multi-agent pipeline.

    Body:
    {
        "resume": "...",
        "job_description": "...",
        "agents": ["analyzer", "career", ...]   // optional – omit for full run
    }
    Auth header optional – if present, injects org dream_companies into Career Agent.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    resume            = data.get("resume", "").strip()
    job_description   = data.get("job_description", "").strip()
    requested_agents  = data.get("agents", [])

    is_valid, err = InputValidator.validate_both(resume, job_description)
    if not is_valid:
        return jsonify({"error": err}), 400

    user_id, org_id, dream_companies = _get_identity()

    try:
        from app.agents.graph import run_full_analysis, run_targeted_analysis

        if requested_agents:
            state = run_targeted_analysis(
                resume, job_description, requested_agents,
                user_id=user_id, org_id=org_id,
            )
        else:
            state = run_full_analysis(
                resume, job_description,
                user_id=user_id, org_id=org_id,
                dream_companies=dream_companies,
            )

        # Persist session if authenticated
        if user_id:
            _persist_session(user_id, org_id, state)

        # Increment session analysis counters if student is in an active TPO session
        if user_id and org_id:
            _increment_session_counters(user_id, org_id)

        return jsonify({
            "success":              True,
            "session_id":           state.get("session_id"),
            "match_percentage":     state.get("match_percentage"),
            "matching_skills":      state.get("matching_skills", []),
            "missing_skills":       state.get("missing_skills", []),
            "skill_gaps":           state.get("skill_gaps", []),
            "has_skill_gaps":       state.get("has_skill_gaps", False),
            "career_fields":        state.get("career_fields", []),
            "job_titles":           state.get("job_titles", []),
            "industries":           state.get("industries", []),
            "improved_resume":      state.get("improved_resume"),
            "improvement_status":   state.get("improvement_status"),
            "critic_iterations":    state.get("critic_iterations", 0),
            "suggested_projects":          state.get("suggested_projects", []),
            "interview_questions":         state.get("interview_questions", []),
            "behavioral_questions":        state.get("behavioral_questions", []),
            "technical_questions":         state.get("technical_questions", []),
            "behavioral_questions_rich":   state.get("behavioral_questions_rich", []),
            "technical_questions_rich":    state.get("technical_questions_rich", []),
            "aptitude_questions":          state.get("aptitude_questions", []),
            "focus_areas":                 state.get("focus_areas", []),
            "prep_tips":                   state.get("prep_tips", []),
            "common_mistakes":             state.get("common_mistakes", []),
            "completed_agents":     state.get("completed_agents", []),
            "agent_history":        state.get("agent_history", []),
            "rag_chunks_count":     len(state.get("rag_chunks", [])),
        }), 200

    except ImportError as e:
        return jsonify({
            "error": "LangGraph not installed. Run: pip install langgraph langchain",
            "detail": str(e),
        }), 501
    except RuntimeError as e:
        err = str(e)
        if "Daily token limit" in err or "tokens per day" in err.lower():
            return jsonify({
                "error": "⏳ Groq daily token quota reached. Please try again in ~1 hour.",
                "quota_exceeded": True,
            }), 503
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": err}), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": f"Agent pipeline failed: {str(e)}"}), 500


def _persist_session(user_id: str, org_id: str, state: dict) -> None:
    """Fire-and-forget session persistence after a pipeline run."""
    try:
        from app.db.models import AgentSession
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            last_node = (state.get("completed_agents") or [""])[-1]
            session = AgentSession(
                user_id=user_id,
                org_id=org_id,
                agent_state={k: v for k, v in state.items()
                             if k not in ("messages",)},  # skip non-serialisable
                last_node=last_node,
                match_pct=state.get("match_percentage"),
                skill_gaps=state.get("skill_gaps", []),
                completed_agents=state.get("completed_agents", []),
                status="completed" if last_node == "interview" else "active",
            )
            db.add(session)
            db.commit()
        finally:
            db.close()
    except Exception as exc:
        print(f"[agents] Session persist skipped: {exc}")


def _increment_session_counters(student_id: str, org_id: str) -> None:
    """
    If the student is a participant in an active TPO session for their org,
    atomically increment both the participant's and the session's analyses_completed counter.
    Fire-and-forget — errors are logged but never propagate to the caller.
    """
    try:
        from app.db.models import SessionParticipant, TPOLiveSession
        from app.db.session import SessionLocal
        from sqlalchemy import update

        db = SessionLocal()
        try:
            participant = (
                db.query(SessionParticipant)
                .join(TPOLiveSession, TPOLiveSession.id == SessionParticipant.session_id)
                .filter(
                    SessionParticipant.student_id == student_id,
                    TPOLiveSession.org_id == org_id,
                    TPOLiveSession.status == "active",
                )
                .first()
            )
            if participant:
                db.execute(
                    update(SessionParticipant)
                    .where(SessionParticipant.id == participant.id)
                    .values(analyses_completed=SessionParticipant.analyses_completed + 1)
                )
                db.execute(
                    update(TPOLiveSession)
                    .where(TPOLiveSession.id == participant.session_id)
                    .values(analyses_completed=TPOLiveSession.analyses_completed + 1)
                )
                db.commit()
        finally:
            db.close()
    except Exception as exc:
        print(f"[agents] Session counter increment skipped: {exc}")


@agents_bp.route("/status", methods=["GET"])
def agent_status():
    """Check if the LangGraph system is available."""
    try:
        import langgraph, langchain
        return jsonify({
            "available":         True,
            "langgraph_version": getattr(langgraph, "__version__", "installed"),
            "langchain_version": getattr(langchain, "__version__", "installed"),
        }), 200
    except ImportError as e:
        return jsonify({
            "available": False,
            "message":   "Install with: pip install langgraph langchain faiss-cpu sentence-transformers",
            "detail":    str(e),
        }), 200
