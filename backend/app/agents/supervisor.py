"""
Master Supervisor – LLM-powered router using structured output.

Uses LangChain's .with_structured_output(RouteDecision) which works with
both ChatOllama (local) and ChatGroq (cloud) without any backend-specific code.

Routing rules:
  1. "analyzer"    must always run first.
  2. has_skill_gaps=True  → "project" must run before "interview".
  3. has_skill_gaps=False → can route directly to "interview".
  4. Never repeat a completed agent.
  5. Return "END" when all required agents have run.
"""
from __future__ import annotations

from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from pydantic import BaseModel, Field

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState


# ── Structured output schema ──────────────────────────────────────────────────

class RouteDecision(BaseModel):
    """Structured output the supervisor must return."""
    next: Literal[
        "analyzer", "career", "improvement", "project",
        "interview", "institutional_analyst", "END"
    ] = Field(
        description="The next agent to invoke. Use 'END' when all required agents have completed."
    )
    reason: str = Field(
        description="One-sentence justification for this routing decision."
    )


# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM = """You are the Master Supervisor of ResumX V2 – a sovereign multi-agent career platform.
Your ONLY job is to decide which specialized agent to invoke next.

Agents available:
  analyzer              – deep skill-gap audit (MUST run first)
  career                – maps skills to career fields and market trends
  improvement           – rewrites resume bullet points (Writer-Critic loop)
  project               – suggests portfolio projects to bridge skill gaps
  interview             – generates behavioral + technical interview questions
  institutional_analyst – TPO-only: generates batch readiness report for a college
  END                   – all required work is complete

Hard routing rules:
  1. If user_intent == "tpo_report" → route to "institutional_analyst" immediately.
  2. If "analyzer" NOT in completed_agents → always route to "analyzer".
  3. If has_skill_gaps=True AND "project" NOT in completed_agents
     AND "interview" NOT in completed_agents → route to "project".
  4. Never route to an agent already in completed_agents.
  5. Route to "END" only when all agents required by user_intent have run.

Respond ONLY with the RouteDecision structured output. No prose."""


# ── Supervisor class ──────────────────────────────────────────────────────────

class SupervisorAgent:
    """
    LLM-powered router with deterministic fallback.

    Uses .with_structured_output(RouteDecision) so the LLM is forced to return
    a valid RouteDecision object – no JSON parsing needed here.
    Works identically with ChatOllama and ChatGroq.
    """

    def decide(self, state: AgentState) -> str:
        completed = state.get("completed_agents", [])
        has_gaps  = state.get("has_skill_gaps", False)
        intent    = state.get("user_intent", "full_analysis")

        # Always use deterministic fallback — avoids structured output entirely.
        # The LLM path was causing SecretStr / compatibility issues with the
        # key-rotation proxy. Deterministic routing is faster and 100% reliable.
        return self._fallback(completed, has_gaps, intent)

    @staticmethod
    def _fallback(completed: list, has_gaps: bool, intent: str = "") -> str:
        """Deterministic pipeline — always runs all 5 agents."""
        if intent == "tpo_report":
            return "END" if "institutional_analyst" in completed else "institutional_analyst"
        # Always run all 5 agents — project runs regardless of has_skill_gaps
        # so users always get project suggestions even with a high match score
        pipeline = ["analyzer", "career", "improvement", "project", "interview"]
        for agent in pipeline:
            if agent not in completed:
                return agent
        return "END"


# ── LangGraph node ────────────────────────────────────────────────────────────

def supervisor_node(state: AgentState) -> dict:
    next_agent = SupervisorAgent().decide(state)
    return {
        "next_agent": next_agent,
        "messages": [AIMessage(content=f"Routing to: {next_agent}", name="supervisor")],
        "agent_history": [{"agent": "supervisor", "action": "route",
                           "result": f"next={next_agent}"}],
    }


def route_from_supervisor(state: AgentState) -> str:
    return state.get("next_agent", "END")
