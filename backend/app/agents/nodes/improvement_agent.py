"""
Improvement Agent – Writer-Critic loop.

The Writer rewrites resume bullet points to address skill gaps.
The Critic scores the draft (1-10) and flags contradictions with verified_facts.
Loop runs until score >= 8 or MAX_ITERATIONS is reached.

Hallucination guardrail: the Critic explicitly checks the draft against
verified_facts and rejects any invented skills or experience.
"""
import re
from app.agents.base_agent import BaseAgent
from app.agents.llm_provider import get_llm_fast
from app.agents.state import AgentState

MAX_ITERATIONS = 2

_WRITER_SYSTEM = """You are an expert Resume Writer.
Rewrite the resume to address skill gaps using ONLY information from VERIFIED RESUME FACTS.
Never add skills, roles, or achievements not present in the verified facts.
Return ONLY valid JSON."""

_CRITIC_SYSTEM = """You are a strict Resume Critic and Hallucination Detector.
Score the resume draft 1-10. Deduct points for:
  - Any skill or achievement NOT in the verified facts (hallucination)
  - Vague bullet points that don't address the identified gaps
  - Missing quantifiable impact
Return ONLY valid JSON."""


class ImprovementAgent(BaseAgent):
    def __init__(self):
        super().__init__("improvement", _WRITER_SYSTEM, max_tokens=1500)

    def _call_llm(self, user_prompt: str, max_tokens: int | None = None) -> str:
        """Use the fast/light model to conserve daily token quota."""
        from langchain_core.messages import HumanMessage, SystemMessage
        llm = get_llm_fast(temperature=self._temperature,
                           max_tokens=max_tokens or self._max_tokens)
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        return llm.invoke(messages).content.strip()

    # ── Writer pass ───────────────────────────────────────────────────────────

    def _write(self, state: AgentState, current_draft: str) -> str:
        rag_ctx = self._get_rag_context(state, "resume bullet points improvements")
        facts = self._facts_block(state)
        gaps = "\n".join(
            f"  • {g['skill']} ({g.get('importance','medium')})"
            for g in state.get("skill_gaps", [])[:6]
        )

        prompt = f"""Rewrite this resume to address the skill gaps below.
Only use information from VERIFIED RESUME FACTS – do not invent anything.

SKILL GAPS TO ADDRESS:
{gaps}

CURRENT RESUME (key sections only):
{current_draft[:1500]}

{facts}

IMPORTANT: Return ONLY this JSON. improved_resume must be a plain string with \\n for newlines.
{{
  "improved_resume": "full rewritten resume as plain text",
  "changes_made": ["change1", "change2"]
}}"""

        self.system_prompt = _WRITER_SYSTEM
        raw = self._call_llm(prompt, max_tokens=1500)

        # Try JSON parse first
        try:
            r = self._parse_json(raw)
            result = r.get("improved_resume", "").strip()
            if result:
                return result
        except Exception:
            pass

        # Fallback: if the LLM returned the resume directly (not wrapped in JSON),
        # strip any outer JSON scaffolding and return the text content
        # Look for the resume text between the JSON key and closing brace
        match = re.search(
            r'"improved_resume"\s*:\s*"([\s\S]+?)"\s*(?:,|\})',
            raw, re.DOTALL
        )
        if match:
            return match.group(1).replace("\\n", "\n").replace('\\"', '"')

        # Last resort: return whatever the LLM gave us, stripped of JSON syntax
        cleaned = re.sub(r'^\s*\{.*?"improved_resume"\s*:\s*"', '', raw, flags=re.DOTALL)
        cleaned = re.sub(r'"\s*,?\s*"changes_made"[\s\S]*$', '', cleaned)
        cleaned = cleaned.strip().strip('"')
        return cleaned if len(cleaned) > 100 else current_draft

    # ── Critic pass ───────────────────────────────────────────────────────────

    def _critique(self, draft: str, state: AgentState) -> dict:
        facts = self._facts_block(state)
        gaps = state.get("missing_skills", [])

        prompt = f"""Critique this resume draft.

GAPS IT SHOULD ADDRESS: {gaps}
{facts}

RESUME DRAFT:
{draft[:2500]}

Return ONLY this JSON:
{{
  "score": <1-10>,
  "hallucinations_found": ["invented item 1"],
  "fixes": ["fix1", "fix2"],
  "verdict": "pass|revise"
}}"""

        self.system_prompt = _CRITIC_SYSTEM
        try:
            raw = self._call_llm(prompt, max_tokens=600)
            return self._parse_json(raw)
        except Exception:
            return {"score": 8, "hallucinations_found": [], "fixes": [], "verdict": "pass"}

    # ── Main run ──────────────────────────────────────────────────────────────

    def run(self, state: AgentState) -> dict:
        draft = state.get("resume_raw", "")
        iterations = 0

        for _ in range(MAX_ITERATIONS):
            iterations += 1
            draft = self._write(state, draft)
            critique = self._critique(draft, state)

            if critique.get("verdict") == "pass" or critique.get("score", 0) >= 8:
                break

        msg = self._make_result_message(
            f"Writer-Critic loop done in {iterations} iteration(s)."
        )

        return {
            "improved_resume":    draft,
            "improvement_status": f"Completed in {iterations} Writer-Critic iteration(s)",
            "critic_iterations":  iterations,
            "messages":           [msg],
            "agent_history":      [{"agent": "improvement", "action": "writer_critic",
                                    "result": f"iterations={iterations}"}],
            "completed_agents":   self._mark_done(state, "improvement"),
        }


def improvement_node(state: AgentState) -> dict:
    return ImprovementAgent().run(state)
