"""
Analyzer Agent – accurate resume-to-JD match scoring.
Uses full resume text (not just RAG chunks) for complete context.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent
from app.agents.llm_provider import get_llm_analyzer
from app.agents.state import AgentState

_SYSTEM = """You are a Senior Technical Recruiter scoring a resume against a job description.

SCORING METHODOLOGY:
1. Extract ALL required skills/tools/concepts from the JD.
2. For each required item, check if the candidate has it (exact OR transferable):
   - Exact match: candidate lists the exact skill → full credit
   - Transferable: candidate has closely related skill → 80% credit
     Examples: FastAPI ↔ Django, LangChain ↔ LlamaIndex, PyTorch ↔ TensorFlow
3. match_percentage = sum(credits) / total_required_items * 100
4. Round to nearest 5.

CALIBRATION EXAMPLES:
- Candidate has 9/10 required skills → 88-92%
- Candidate has 7/10 required skills → 72-78%
- Candidate has 5/10 required skills → 52-58%

CRITICAL RULES:
- Use the FULL resume text provided — do not ignore any section.
- "Nice to have" / "bonus" / "preferred" items are optional — missing them does NOT reduce score.
- Only list a skill under missing_skills if it is COMPLETELY absent from the resume.
- Return ONLY valid JSON."""


class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("analyzer", _SYSTEM)

    def _call_llm(self, user_prompt: str, max_tokens: int | None = None) -> str:
        llm = get_llm_analyzer(temperature=0.1, max_tokens=max_tokens or 1500)
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        raw = llm.invoke(messages).content.strip()
        print(f"[Analyzer] score preview: {raw[:120]}")
        return raw

    def run(self, state: AgentState) -> dict:
        # Use FULL resume — not just RAG chunks — for accurate scoring
        resume   = state.get("resume_raw", "")
        jd       = state.get("job_description", "")
        facts    = self._facts_block(state)

        prompt = f"""Score this resume against the job description using the methodology in your instructions.

=== JOB DESCRIPTION ===
{jd}

=== FULL RESUME ===
{resume[:4000]}
{facts}

Step 1: List every required skill/tool from the JD.
Step 2: For each, mark exact_match / transferable / missing.
Step 3: Calculate match_percentage = credits / total * 100.

Return ONLY this JSON (no prose outside it):
{{
  "match_percentage": <0-100, rounded to nearest 5>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["only truly absent skills"],
  "skill_gaps": [{{"skill": "name", "importance": "high|medium|low"}}],
  "key_strengths": ["strength1", "strength2"],
  "feedback": "2-3 sentence honest assessment",
  "improvements": ["actionable suggestion1"],
  "summary": "one sentence verdict"
}}"""

        try:
            raw = self._call_llm(prompt, max_tokens=1500)
            r   = self._parse_json(raw)

            pct = r.get("match_percentage", 0)
            # Sanity: if LLM returned 0 but found matching skills, recalculate
            if pct == 0 and r.get("matching_skills"):
                pct = min(95, max(40, len(r["matching_skills"]) * 9))
                r["match_percentage"] = pct
                print(f"[Analyzer] Corrected 0% → {pct}%")

        except Exception as e:
            print(f"[Analyzer] Failed: {e}")
            r = {
                "match_percentage": 0, "matching_skills": [], "missing_skills": [],
                "skill_gaps": [], "key_strengths": [], "feedback": str(e),
                "improvements": [], "summary": "Analysis failed — please retry.",
            }

        has_gaps = bool(r.get("missing_skills"))
        return {
            "match_percentage": r.get("match_percentage", 0),
            "matching_skills":  r.get("matching_skills", []),
            "missing_skills":   r.get("missing_skills", []),
            "skill_gaps":       r.get("skill_gaps", []),
            "has_skill_gaps":   has_gaps,
            "messages":         [self._make_result_message(
                f"Match={r.get('match_percentage')}%, gaps={len(r.get('missing_skills', []))}"
            )],
            "agent_history":    [{"agent": "analyzer", "action": "audit",
                                  "result": f"match={r.get('match_percentage')}%"}],
            "completed_agents": self._mark_done(state, "analyzer"),
        }


def analyzer_node(state: AgentState) -> dict:
    return AnalyzerAgent().run(state)
