"""
ResumX V2 – LangGraph Multi-Agent Graph
========================================

V2 Flow:
  START
    │
    ▼
  [init]  ← indexes resume+JD into FAISS, extracts verified_facts
    │
    ├─ resume missing? ──► [resume_creator]  (onboarding chatbot)
    │                            │
    │                      onboarding_complete=True
    │                            │
    ▼                            ▼
  [supervisor]  ← LLM-powered router
    │
    ├─► analyzer            ─┐
    ├─► career               ├──► back to [supervisor]
    ├─► improvement          │
    ├─► project              │
    ├─► interview            │
    ├─► institutional_analyst─┘  (TPO-only node)
    │
    └─► END

Conditional routing:
  - No resume → resume_creator first
  - user_intent == "tpo_report" → institutional_analyst
  - has_skill_gaps=True → project before interview
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from app.agents.nodes import (
    analyzer_node,
    career_node,
    creator_node,
    improvement_node,
    institutional_analyst_node,
    interview_node,
    project_node,
)
from app.agents.rag_store import RAGStore
from app.agents.state import AgentState
from app.agents.supervisor import route_from_supervisor, supervisor_node


# ── Analytics Counter Node ────────────────────────────────────────────────────

def _analytics_counter_node(state: AgentState) -> dict:
    """
    Post-processing node that runs after a successful AnalyzerAgent run.
    - Atomically increments Organization.total_resumes_analyzed
    - Inserts an AnalysisLog row with run metadata
    Silently no-ops if org_id is absent (unauthenticated / local-mode runs).
    """
    org_id     = state.get("org_id")
    user_id    = state.get("user_id")
    match_pct  = state.get("match_percentage")

    if org_id:
        try:
            from app.db.session import SessionLocal
            from app.services.analytics_service import record_analysis
            from app.agents.llm_provider import GROQ_MODEL_ANALYZER

            db = SessionLocal()
            try:
                record_analysis(
                    db,
                    org_id=org_id,
                    student_id=user_id,
                    model_used=GROQ_MODEL_ANALYZER,
                    match_score=float(match_pct) if match_pct is not None else None,
                )
            finally:
                db.close()
        except Exception as exc:
            # Never let analytics failure break the main pipeline
            print(f"[AnalyticsCounter] non-fatal error: {exc}")

    return {}  # no state mutation needed


# ── Init node ─────────────────────────────────────────────────────────────────

def _init_node(state: AgentState) -> dict:
    """
    Entry node – runs once per session.
    If resume_raw is empty, skips RAG indexing (creator_node will do it later).
    """
    resume = state.get("resume_raw", "").strip()
    jd     = state.get("job_description", "")

    if resume:
        store   = RAGStore.reset()
        chunks  = store.index_documents(resume, jd)
        facts   = store.extract_verified_facts(resume)
        rag_ctx = store.retrieve_as_context(
            f"skills experience projects {jd[:200]}", top_k=6
        )
    else:
        chunks, facts, rag_ctx = [], [], ""

    return {
        "rag_chunks":       chunks,
        "rag_context":      rag_ctx,
        "verified_facts":   facts,
        "completed_agents": state.get("completed_agents") or [],
        "onboarding_complete": bool(resume),
        "messages": [HumanMessage(
            content=(
                f"Session started. "
                f"{'Resume indexed' if resume else 'No resume – starting onboarding'}. "
                f"chunks={len(chunks)}, facts={len(facts)}"
            ),
            name="init",
        )],
        "agent_history": [{
            "agent":  "init",
            "action": "rag_indexing",
            "result": f"chunks={len(chunks)}, facts={len(facts)}, has_resume={bool(resume)}",
        }],
    }


def _route_after_init(state: AgentState) -> str:
    """After init: go to onboarding if no resume, else straight to supervisor."""
    if not state.get("onboarding_complete", False):
        return "resume_creator"
    return "supervisor"


def _route_after_creator(state: AgentState) -> str:
    """After each creator turn: loop back until onboarding is complete."""
    if state.get("onboarding_complete", False):
        return "supervisor"
    return "resume_creator"


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    # Nodes
    g.add_node("init",                  _init_node)
    g.add_node("resume_creator",        creator_node)
    g.add_node("supervisor",            supervisor_node)
    g.add_node("analyzer",              analyzer_node)
    g.add_node("analytics_counter",     _analytics_counter_node)
    g.add_node("career",                career_node)
    g.add_node("improvement",           improvement_node)
    g.add_node("project",               project_node)
    g.add_node("interview",             interview_node)
    g.add_node("institutional_analyst", institutional_analyst_node)

    # Entry
    g.set_entry_point("init")

    # init → onboarding OR supervisor
    g.add_conditional_edges(
        "init",
        _route_after_init,
        {"resume_creator": "resume_creator", "supervisor": "supervisor"},
    )

    # creator loops until onboarding done
    g.add_conditional_edges(
        "resume_creator",
        _route_after_creator,
        {"resume_creator": "resume_creator", "supervisor": "supervisor"},
    )

    # All specialist nodes loop back to supervisor
    # analyzer → analytics_counter → supervisor (for the counter side-effect)
    g.add_edge("analyzer", "analytics_counter")
    g.add_edge("analytics_counter", "supervisor")
    for node in ("career", "improvement", "project",
                 "interview", "institutional_analyst"):
        g.add_edge(node, "supervisor")

    # Supervisor conditional routing
    g.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "analyzer":             "analyzer",
            "career":               "career",
            "improvement":          "improvement",
            "project":              "project",
            "interview":            "interview",
            "institutional_analyst": "institutional_analyst",
            "END":                  END,
        },
    )

    return g.compile()


# ── Singleton compiled graph ──────────────────────────────────────────────────

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


# ── Initial state factory ─────────────────────────────────────────────────────

def _make_initial_state(
    resume: str,
    job_description: str,
    intent: str,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    session_id: Optional[str] = None,
    dream_companies: Optional[List[str]] = None,
    batch_records: Optional[List[Dict]] = None,
    existing_state: Optional[Dict] = None,
) -> AgentState:
    """
    Build the initial AgentState.
    Pass existing_state to resume a persisted session from the DB.
    """
    base: Dict[str, Any] = {
        "user_id":    user_id,
        "org_id":     org_id,
        "session_id": session_id,

        "messages":   [],
        "resume_raw": resume,
        "job_description": job_description,

        "onboarding_complete":  bool(resume.strip()),
        "creator_conversation": [],

        "rag_context":    "",
        "rag_chunks":     [],
        "verified_facts": [],

        "match_percentage": None,
        "matching_skills":  [],
        "missing_skills":   [],
        "skill_gaps":       [],
        "has_skill_gaps":   False,

        "career_fields":   [],
        "job_titles":      [],
        "industries":      [],
        "dream_companies": dream_companies or [],

        "improved_resume":    None,
        "improvement_status": None,
        "critic_iterations":  0,

        "suggested_projects":  [],
        "interview_questions": [],
        "behavioral_questions": [],
        "technical_questions":  [],
        "behavioral_questions_rich": [],
        "technical_questions_rich":  [],
        "focus_areas":          [],
        "prep_tips":            [],
        "common_mistakes":      [],

        "batch_records": batch_records or [],
        "batch_report":  None,

        "next_agent":       None,
        "completed_agents": [],
        "user_intent":      intent,
        "agent_history":    [],
        "error":            None,
    }

    # Merge persisted state on top (resume session)
    if existing_state:
        base.update({k: v for k, v in existing_state.items() if v is not None})

    return AgentState(**base)


# ── Public API ────────────────────────────────────────────────────────────────

def run_full_analysis(
    resume: str,
    job_description: str,
    user_id: str = None,
    org_id: str = None,
    session_id: str = None,
    dream_companies: List[str] = None,
) -> Dict[str, Any]:
    """Run the complete student pipeline (all 5 specialist agents)."""
    state = _make_initial_state(
        resume, job_description, "full_analysis",
        user_id=user_id, org_id=org_id, session_id=session_id,
        dream_companies=dream_companies,
    )
    return get_graph().invoke(state)


def run_targeted_analysis(
    resume: str,
    job_description: str,
    agents: List[str],
    user_id: str = None,
    org_id: str = None,
) -> Dict[str, Any]:
    """Run only the specified agents; supervisor still enforces ordering."""
    state = _make_initial_state(
        resume, job_description,
        f"run_agents:{','.join(agents)}",
        user_id=user_id, org_id=org_id,
    )
    return get_graph().invoke(state)


def run_tpo_report(
    org_id: str,
    batch_records: List[Dict],
    dream_companies: List[str] = None,
) -> Dict[str, Any]:
    """Run the InstitutionalAnalyst node for a TPO batch report."""
    state = _make_initial_state(
        "", "", "tpo_report",
        org_id=org_id,
        dream_companies=dream_companies,
        batch_records=batch_records,
    )
    return get_graph().invoke(state)


def resume_session(
    session_id: str,
    persisted_state: Dict[str, Any],
    new_user_message: str = "",
) -> Dict[str, Any]:
    """
    Resume a persisted LangGraph session from the database.
    Merges the stored state and continues from the last node.
    """
    state = _make_initial_state(
        persisted_state.get("resume_raw", ""),
        persisted_state.get("job_description", ""),
        persisted_state.get("user_intent", "full_analysis"),
        user_id=persisted_state.get("user_id"),
        org_id=persisted_state.get("org_id"),
        session_id=session_id,
        existing_state=persisted_state,
    )
    if new_user_message:
        from langchain_core.messages import HumanMessage
        state["messages"] = [HumanMessage(content=new_user_message)]
    return get_graph().invoke(state)
