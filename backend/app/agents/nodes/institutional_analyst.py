"""
ResumX V2 – InstitutionalAnalyst Agent (TPO Node)
==================================================

Triggered when: user_intent == "tpo_report" (role = "tpo").

Behaviour:
  1. Reads batch_records from state (pre-loaded from DB by the route handler
     using AgentSession rows filtered by org_id).
  2. Aggregates skill gaps, match percentages, and readiness metrics
     across all students in the batch.
  3. Calls the LLM to generate a narrative Batch Readiness Report.
  4. Writes the report to batch_report in state.
  5. The route handler persists the result to TPOReport table.

batch_records shape (injected by route):
  [
    {
      "user_id": "...",
      "full_name": "...",
      "match_pct": 72.0,
      "skill_gaps": ["Docker", "Kubernetes"],
      "completed_agents": ["analyzer", "career", ...]
    },
    ...
  ]
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict, List

from langchain_core.messages import AIMessage

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState

_SYSTEM = """You are the ResumX Institutional Analyst – a senior placement consultant
advising a college's Training & Placement Office (TPO).

You receive aggregated skill-gap data for an entire student batch and must produce
a concise, actionable Batch Readiness Report.

The report must include:
  1. Executive Summary (3-4 sentences)
  2. Top 10 Skill Gaps (ranked by frequency across the batch)
  3. Match Percentage Distribution (buckets: <40%, 40-60%, 60-80%, >80%)
  4. Batch Readiness Score (0-100, weighted composite)
  5. Recommended Interventions (specific workshops / courses to close top gaps)
  6. Dream Company Alignment (how many students are ready for each dream company)

Return ONLY valid JSON. No prose outside the JSON block."""


class InstitutionalAnalystAgent(BaseAgent):

    def __init__(self) -> None:
        super().__init__(
            "institutional_analyst", _SYSTEM,
            temperature=0.3, max_tokens=4000,
        )

    def run(self, state: AgentState) -> dict:
        records: List[Dict[str, Any]] = state.get("batch_records") or []
        dream_companies: List[str]    = state.get("dream_companies") or []

        if not records:
            return self._empty_report(state)

        # ── Aggregate metrics ─────────────────────────────────────────────────
        aggregated = self._aggregate(records)

        prompt = f"""Generate a Batch Readiness Report for the following batch data.

BATCH SIZE: {aggregated['total_students']} students
AVERAGE MATCH PERCENTAGE: {aggregated['avg_match_pct']:.1f}%
DREAM COMPANIES: {', '.join(dream_companies) or 'Not configured'}

TOP SKILL GAPS (skill → count of students missing it):
{json.dumps(aggregated['top_skill_gaps'], indent=2)}

MATCH DISTRIBUTION:
{json.dumps(aggregated['match_distribution'], indent=2)}

STUDENT RECORDS (anonymised):
{json.dumps(aggregated['student_summaries'], indent=2)}

Return ONLY this JSON:
{{
  "executive_summary": "...",
  "batch_readiness_score": <0-100>,
  "top_skill_gaps": [
    {{"rank": 1, "skill": "...", "affected_students": N, "priority": "critical|high|medium"}}
  ],
  "match_distribution": {{
    "below_40": N, "40_to_60": N, "60_to_80": N, "above_80": N
  }},
  "recommended_interventions": [
    {{"skill": "...", "resource": "...", "duration": "..."}}
  ],
  "dream_company_alignment": [
    {{"company": "...", "ready_students": N, "readiness_pct": <0-100>}}
  ],
  "generated_for_org_id": "{state.get('org_id', 'unknown')}"
}}"""

        try:
            raw    = self._call_llm(prompt, max_tokens=4000)
            report = self._parse_json(raw)
        except Exception as exc:
            report = {
                "executive_summary": f"Report generation failed: {exc}",
                "batch_readiness_score": 0,
                "top_skill_gaps": aggregated["top_skill_gaps"],
                "match_distribution": aggregated["match_distribution"],
                "recommended_interventions": [],
                "dream_company_alignment": [],
                "generated_for_org_id": state.get("org_id", "unknown"),
            }

        # Attach raw aggregation for CSV export
        report["_raw_aggregation"] = aggregated

        return {
            "batch_report": report,
            "messages": [AIMessage(
                content=(
                    f"Batch report generated. "
                    f"Readiness score: {report.get('batch_readiness_score', 'N/A')}/100. "
                    f"Students analysed: {aggregated['total_students']}."
                ),
                name="institutional_analyst",
            )],
            "agent_history": [{
                "agent":  "institutional_analyst",
                "action": "batch_report",
                "result": (
                    f"score={report.get('batch_readiness_score')}, "
                    f"students={aggregated['total_students']}"
                ),
            }],
            "completed_agents": self._mark_done(state, "institutional_analyst"),
        }

    # ── Aggregation helpers ───────────────────────────────────────────────────

    def _aggregate(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(records)
        match_pcts = [r.get("match_pct", 0) for r in records]
        avg_match  = sum(match_pcts) / total if total else 0

        # Skill gap frequency
        gap_counter: Counter = Counter()
        for r in records:
            for gap in r.get("skill_gaps", []):
                skill = gap if isinstance(gap, str) else gap.get("skill", "")
                if skill:
                    gap_counter[skill] += 1

        top_gaps = [
            {"skill": skill, "count": count}
            for skill, count in gap_counter.most_common(10)
        ]

        # Match distribution buckets
        dist = {"below_40": 0, "40_to_60": 0, "60_to_80": 0, "above_80": 0}
        for pct in match_pcts:
            if pct < 40:
                dist["below_40"] += 1
            elif pct < 60:
                dist["40_to_60"] += 1
            elif pct < 80:
                dist["60_to_80"] += 1
            else:
                dist["above_80"] += 1

        # Anonymised student summaries (no PII in LLM prompt)
        student_summaries = [
            {
                "id":         i + 1,
                "match_pct":  r.get("match_pct", 0),
                "gap_count":  len(r.get("skill_gaps", [])),
                "top_gaps":   (r.get("skill_gaps") or [])[:3],
            }
            for i, r in enumerate(records)
        ]

        return {
            "total_students":   total,
            "avg_match_pct":    avg_match,
            "top_skill_gaps":   top_gaps,
            "match_distribution": dist,
            "student_summaries": student_summaries,
        }

    def _empty_report(self, state: AgentState) -> dict:
        report = {
            "executive_summary": "No student data available for this organisation yet.",
            "batch_readiness_score": 0,
            "top_skill_gaps": [],
            "match_distribution": {"below_40": 0, "40_to_60": 0, "60_to_80": 0, "above_80": 0},
            "recommended_interventions": [],
            "dream_company_alignment": [],
            "generated_for_org_id": state.get("org_id", "unknown"),
        }
        return {
            "batch_report": report,
            "messages": [AIMessage(
                content="No batch data found for this organisation.",
                name="institutional_analyst",
            )],
            "agent_history": [{"agent": "institutional_analyst",
                                "action": "empty_report", "result": "no data"}],
            "completed_agents": self._mark_done(state, "institutional_analyst"),
        }


def institutional_analyst_node(state: AgentState) -> dict:
    return InstitutionalAnalystAgent().run(state)
