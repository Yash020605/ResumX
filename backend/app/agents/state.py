"""
AgentState V2 – Multi-Tenant LangGraph State
=============================================

New V2 fields:
  - user_id / org_id / session_id  : multi-tenant identity
  - dream_companies                : TPO-configured target companies
  - onboarding_complete            : flag for ResumeCreator flow
  - creator_conversation           : message history for onboarding chatbot
  - batch_report                   : InstitutionalAnalyst output (TPO node)
"""
from __future__ import annotations

import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage


# ── Sub-schemas ───────────────────────────────────────────────────────────────

class SkillGap(TypedDict):
    skill: str
    importance: str          # "high" | "medium" | "low"


class AgentEvent(TypedDict):
    agent: str
    action: str
    result: str


class ProjectSuggestion(TypedDict):
    title: str
    description: str
    tech_stack: List[str]
    skills_addressed: List[str]
    difficulty: str          # "beginner" | "intermediate" | "advanced"
    why_recommended: str
    first_steps: List[str]


class StudentBatchRecord(TypedDict):
    """One student's contribution to the TPO batch report."""
    user_id: str
    full_name: str
    match_pct: float
    skill_gaps: List[str]
    completed_agents: List[str]


# ── Main state ────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    # ── Multi-tenant identity ────────────────────────────────────────────────
    user_id:    Optional[str]
    org_id:     Optional[str]
    session_id: Optional[str]

    # ── A2A message bus ──────────────────────────────────────────────────────
    messages: Annotated[List[BaseMessage], operator.add]

    # ── Raw inputs ───────────────────────────────────────────────────────────
    resume_raw:      str
    job_description: str

    # ── Onboarding (ResumeCreator) ───────────────────────────────────────────
    onboarding_complete:    bool
    creator_conversation:   List[Dict[str, str]]   # [{"role": "...", "content": "..."}]

    # ── RAG layer ────────────────────────────────────────────────────────────
    rag_context:    str
    rag_chunks:     List[str]
    verified_facts: List[str]

    # ── Analyzer outputs ─────────────────────────────────────────────────────
    match_percentage: Optional[int]
    matching_skills:  List[str]
    missing_skills:   List[str]
    skill_gaps:       List[SkillGap]
    has_skill_gaps:   bool

    # ── Career agent outputs (TPO-tuned) ─────────────────────────────────────
    career_fields:   List[Dict[str, Any]]
    job_titles:      List[str]
    industries:      List[str]
    dream_companies: List[str]   # injected from Organization.dream_companies

    # ── Improvement agent outputs ────────────────────────────────────────────
    improved_resume:    Optional[str]
    improvement_status: Optional[str]
    critic_iterations:  int

    # ── Project agent outputs ────────────────────────────────────────────────
    suggested_projects: List[ProjectSuggestion]

    # ── Interview agent outputs (context-aware of suggested_projects) ────────
    interview_questions:       List[str]
    behavioral_questions:      List[str]
    technical_questions:       List[str]
    behavioral_questions_rich: List[Dict[str, Any]]
    technical_questions_rich:  List[Dict[str, Any]]
    aptitude_questions:        List[Dict[str, Any]]
    focus_areas:               List[str]
    prep_tips:                 List[str]
    common_mistakes:           List[str]

    # ── Institutional Analyst (TPO node) ─────────────────────────────────────
    batch_records:  List[StudentBatchRecord]   # aggregated from DB by TPO node
    batch_report:   Optional[Dict[str, Any]]   # final report payload

    # ── Routing / audit ──────────────────────────────────────────────────────
    next_agent:       Optional[str]
    completed_agents: List[str]
    user_intent:      str
    agent_history:    Annotated[List[AgentEvent], operator.add]
    error:            Optional[str]
