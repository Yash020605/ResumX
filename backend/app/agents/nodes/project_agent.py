"""
Project Idea Agent – suggests portfolio projects that bridge skill gaps.
Uses llama-4-scout (500K TPD).
"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent
from app.agents.llm_provider import get_llm
from app.agents.state import AgentState

_SYSTEM = """You are a Senior Software Engineering Mentor.
Suggest practical portfolio projects that directly bridge the candidate's skill gaps.
Every suggestion must build on skills already present in VERIFIED RESUME FACTS.
Return ONLY valid JSON."""


class ProjectAgent(BaseAgent):
    def __init__(self):
        super().__init__("project", _SYSTEM)

    def _call_llm(self, user_prompt: str, max_tokens: int | None = None) -> str:
        llm = get_llm(temperature=0.4, max_tokens=max_tokens or 1800)
        messages = [SystemMessage(content=self.system_prompt), HumanMessage(content=user_prompt)]
        return llm.invoke(messages).content.strip()

    def run(self, state: AgentState) -> dict:
        missing = state.get("missing_skills", [])
        matching = state.get("matching_skills", [])
        rag_ctx = self._get_rag_context(
            state, f"projects portfolio {' '.join(missing[:5])}"
        )
        facts = self._facts_block(state)

        prompt = f"""Suggest 3-5 portfolio projects for this candidate.

SKILL GAPS TO BRIDGE: {missing}
EXISTING SKILLS (leverage these): {matching}
RAG CONTEXT: {rag_ctx}
{facts}

Return ONLY this JSON:
{{
  "projects": [
    {{
      "title": "Project Name",
      "description": "what it does",
      "tech_stack": ["tech1", "tech2"],
      "skills_addressed": ["gap1", "gap2"],
      "difficulty": "beginner|intermediate|advanced",
      "estimated_duration": "X weeks",
      "why_recommended": "grounded explanation referencing their background",
      "first_steps": ["step1", "step2", "step3"]
    }}
  ]
}}"""

        try:
            raw = self._call_llm(prompt, max_tokens=1800)
            r = self._parse_json(raw)
            # LLM returns {"projects": [...]} — unwrap it
            projects = r.get("projects", r.get("suggested_projects", []))
            if not isinstance(projects, list):
                projects = []
        except Exception as e:
            projects = [{
                "title": "Skill-Bridge Project",
                "description": f"Project targeting: {', '.join(missing[:3])}",
                "tech_stack": missing[:3],
                "skills_addressed": missing[:3],
                "difficulty": "intermediate",
                "estimated_duration": "4 weeks",
                "why_recommended": "Directly targets your identified skill gaps.",
                "first_steps": ["Research the stack", "Build a prototype", "Deploy and document"],
            }]

        msg = self._make_result_message(
            f"Suggested {len(projects)} projects for {len(missing)} skill gaps."
        )

        return {
            "suggested_projects": projects,
            "messages":           [msg],
            "agent_history":      [{"agent": "project", "action": "suggest",
                                    "result": f"projects={len(projects)}"}],
            "completed_agents":   self._mark_done(state, "project"),
        }


def project_node(state: AgentState) -> dict:
    return ProjectAgent().run(state)
