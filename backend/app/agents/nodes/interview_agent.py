"""
Interview Prep Agent – generates behavioral + technical + aptitude questions.
Uses two separate LLM calls to avoid token limit issues:
  Call 1: behavioral + technical + focus areas + tips
  Call 2: aptitude questions
"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent
from app.agents.llm_provider import get_llm
from app.agents.state import AgentState

_SYSTEM = """You are a Senior Technical Interviewer at a top-tier tech company.
Generate realistic, role-specific interview questions with impact context.
Return ONLY valid JSON. No prose outside the JSON block."""

_APTITUDE_SYSTEM = """You are an aptitude test expert for MNC campus placements.
Generate aptitude questions with complete solutions.
Return ONLY valid JSON. No prose outside the JSON block."""


class InterviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("interview", _SYSTEM)

    def _call_llm(self, user_prompt: str, max_tokens: int | None = None) -> str:
        llm = get_llm(temperature=0.4, max_tokens=max_tokens or 2500)
        messages = [SystemMessage(content=self.system_prompt), HumanMessage(content=user_prompt)]
        return llm.invoke(messages).content.strip()

    def _call_aptitude_llm(self, user_prompt: str) -> str:
        llm = get_llm(temperature=0.3, max_tokens=2000)
        messages = [SystemMessage(content=_APTITUDE_SYSTEM), HumanMessage(content=user_prompt)]
        return llm.invoke(messages).content.strip()

    def run(self, state: AgentState) -> dict:
        projects = [p.get("title", "") for p in state.get("suggested_projects", [])]
        matching = state.get("matching_skills", [])
        missing  = state.get("missing_skills", [])
        jd       = state.get("job_description", "")[:400]
        facts    = self._facts_block(state)

        # ── Call 1: Behavioral + Technical ───────────────────────────────────
        prompt1 = f"""Generate interview prep questions for this candidate.

MATCHING SKILLS: {matching}
SKILL GAPS: {missing}
SUGGESTED PROJECTS: {projects}
JOB DESCRIPTION: {jd}
{facts}

Return ONLY this JSON (5 behavioral + 5 technical minimum):
{{
  "behavioral_questions": [
    {{
      "question": "Tell me about a time you...",
      "why_asked": "Assesses X skill",
      "impact": "Strong answer differentiates because...",
      "hint": "Use STAR method focusing on..."
    }}
  ],
  "technical_questions": [
    {{
      "question": "How would you implement...",
      "why_asked": "Tests understanding of X",
      "impact": "Filters candidates who lack X",
      "expected_depth": "brief|detailed",
      "topic": "topic area"
    }}
  ],
  "focus_areas": ["area1", "area2", "area3"],
  "prep_tips": ["tip1", "tip2", "tip3"],
  "common_mistakes": ["mistake1", "mistake2"]
}}"""

        try:
            raw1 = self._call_llm(prompt1, max_tokens=2500)
            r = self._parse_json(raw1)
        except Exception as e:
            print(f"[Interview] Call 1 parse error: {e}")
            r = {
                "behavioral_questions": [], "technical_questions": [],
                "focus_areas": [], "prep_tips": [], "common_mistakes": []
            }

        # ── Call 2: Aptitude Questions ────────────────────────────────────────
        prompt2 = """Generate 6 aptitude questions for MNC campus placement tests.

Return ONLY this JSON:
{
  "aptitude_questions": [
    {
      "question": "A train travels 60 km in 1 hour at uniform speed...",
      "category": "quantitative",
      "difficulty": "easy",
      "answer": "The correct answer is X",
      "explanation": "Step 1: ... Step 2: ... Therefore answer is X",
      "tip": "For speed-distance problems always use formula..."
    }
  ]
}

Include exactly:
- 2 quantitative (speed/time/work/percentages/profit-loss)
- 2 logical reasoning (number series/patterns/syllogisms)
- 1 verbal (sentence correction or analogy)
- 1 data interpretation (simple table or ratio based)
Each must have a complete step-by-step explanation."""

        aptitude_objs = []
        try:
            raw2 = self._call_aptitude_llm(prompt2)
            r2 = self._parse_json(raw2)
            aptitude_objs = r2.get("aptitude_questions", [])
        except Exception as e:
            print(f"[Interview] Aptitude parse error: {e}")

        # ── Flatten for voice interview ────────────────────────────────────────
        behavioral_objs = r.get("behavioral_questions", [])
        technical_objs  = r.get("technical_questions", [])

        def _q(obj): return obj.get("question", obj) if isinstance(obj, dict) else obj

        behavioral_flat = [_q(q) for q in behavioral_objs]
        technical_flat  = [_q(q) for q in technical_objs]

        total = len(behavioral_flat) + len(technical_flat) + len(aptitude_objs)
        print(f"[Interview] Done: {len(behavioral_flat)}B + {len(technical_flat)}T + {len(aptitude_objs)}A = {total}")

        return {
            "behavioral_questions":      behavioral_flat,
            "technical_questions":       technical_flat,
            "interview_questions":       behavioral_flat + technical_flat,
            "behavioral_questions_rich": behavioral_objs,
            "technical_questions_rich":  technical_objs,
            "aptitude_questions":        aptitude_objs,
            "focus_areas":               r.get("focus_areas", []),
            "prep_tips":                 r.get("prep_tips", []),
            "common_mistakes":           r.get("common_mistakes", []),
            "messages": [self._make_result_message(
                f"Interview prep: {len(behavioral_flat)}B + {len(technical_flat)}T + {len(aptitude_objs)}A"
            )],
            "agent_history": [{"agent": "interview", "action": "prep",
                               "result": f"total={total}"}],
            "completed_agents": self._mark_done(state, "interview"),
        }


def interview_node(state: AgentState) -> dict:
    return InterviewAgent().run(state)
