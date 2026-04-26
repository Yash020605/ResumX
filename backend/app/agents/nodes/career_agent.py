"""
Career Field Agent – maps verified skills to rich career paths.
Uses llama-4-scout (500K TPD) for high quota headroom.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent
from app.agents.llm_provider import get_llm
from app.agents.state import AgentState

_SYSTEM = """You are a Career Strategist with deep knowledge of tech hiring trends in India and globally.
Map the candidate's skills to detailed, actionable career paths.
Return ONLY valid JSON."""


class CareerAgent(BaseAgent):
    def __init__(self):
        super().__init__("career", _SYSTEM)

    def _call_llm(self, user_prompt: str, max_tokens: int | None = None) -> str:
        llm = get_llm(temperature=0.4, max_tokens=max_tokens or 2000)
        messages = [SystemMessage(content=self.system_prompt), HumanMessage(content=user_prompt)]
        return llm.invoke(messages).content.strip()

    def run(self, state: AgentState) -> dict:
        rag_ctx = self._get_rag_context(state, "career roles industry experience")
        facts = self._facts_block(state)
        matching = ", ".join(state.get("matching_skills", []))
        dream_cos = state.get("dream_companies", [])
        dream_section = (
            f"\nPRIORITY DREAM COMPANIES: {dream_cos}" if dream_cos else ""
        )

        prompt = f"""Generate detailed career path recommendations for this candidate.

VERIFIED MATCHING SKILLS: {matching}{dream_section}
RAG CONTEXT: {rag_ctx}
{facts}

Return ONLY this JSON:
{{
  "career_fields": [
    {{
      "field": "field name",
      "explanation": "why this fits the candidate (2-3 sentences)",
      "market_demand": "high|medium|low",
      "avg_salary_inr": "e.g. ₹12-25 LPA",
      "avg_salary_usd": "e.g. $90k-140k",
      "top_companies": ["Company1", "Company2", "Company3", "Company4", "Company5"],
      "roadmap": ["Step 1: ...", "Step 2: ...", "Step 3: ...", "Step 4: ..."],
      "certifications": ["Cert 1", "Cert 2"],
      "time_to_ready": "e.g. 3-6 months"
    }}
  ],
  "job_titles": ["title1", "title2", "title3"],
  "industries": ["industry1", "industry2"],
  "growth_opportunities": ["opportunity1", "opportunity2"],
  "recommended_skills": ["skill1", "skill2"],
  "summary": "2-sentence career summary"
}}"""

        try:
            raw = self._call_llm(prompt, max_tokens=2000)
            r = self._parse_json(raw)
        except Exception as e:
            r = {"career_fields": [], "job_titles": [], "industries": [],
                 "growth_opportunities": [], "recommended_skills": [],
                 "certifications": [], "summary": str(e)}

        msg = self._make_result_message(
            f"Career mapping done. Fields={len(r.get('career_fields', []))}"
        )

        return {
            "career_fields":  r.get("career_fields", []),
            "job_titles":     r.get("job_titles", []),
            "industries":     r.get("industries", []),
            "messages":       [msg],
            "agent_history":  [{"agent": "career", "action": "mapping",
                                "result": f"fields={len(r.get('career_fields', []))}"}],
            "completed_agents": self._mark_done(state, "career"),
        }


def career_node(state: AgentState) -> dict:
    return CareerAgent().run(state)
