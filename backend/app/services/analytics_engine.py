"""
Analytics Engine – Batch-Level Skill Heatmap & Readiness Score
================================================================

Responsibilities:
  1. compute_skill_heatmap()  – frequency analysis of matching/missing skills
  2. compute_readiness_score() – weighted formula for placement readiness
  3. generate_actionable_insight() – dynamic text based on score + skill gaps
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List

from sqlalchemy.orm import Session

from app.db.models import AgentSession, Organization, User


def compute_skill_heatmap(db: Session, org_id: str) -> Dict[str, List[Dict]]:
    """
    Aggregates skills across all students in an org.

    Returns:
      {
        "top_matching_skills": [{"skill": "Python", "count": 45, "pct": 90}, ...],
        "top_missing_skills":  [{"skill": "Docker", "count": 38, "pct": 76}, ...]
      }
    """
    users = db.query(User).filter_by(org_id=org_id, is_active=True, role="student").all()
    total_students = len(users)

    if total_students == 0:
        return {"top_matching_skills": [], "top_missing_skills": []}

    matching_counter = Counter()
    missing_counter = Counter()

    for user in users:
        session = (
            db.query(AgentSession)
            .filter_by(user_id=user.id)
            .order_by(AgentSession.updated_at.desc())
            .first()
        )
        if not session or not session.agent_state:
            continue

        state = session.agent_state
        matching_skills = state.get("matching_skills", [])
        missing_skills = state.get("missing_skills", [])

        for skill in matching_skills:
            matching_counter[skill] += 1

        for skill in missing_skills:
            missing_counter[skill] += 1

    def _format(counter: Counter, limit: int = 10) -> List[Dict]:
        return [
            {
                "skill": skill,
                "count": count,
                "pct": round((count / total_students) * 100, 1),
            }
            for skill, count in counter.most_common(limit)
        ]

    return {
        "top_matching_skills": _format(matching_counter, 10),
        "top_missing_skills": _format(missing_counter, 10),
        "total_students": total_students,
    }


def compute_readiness_score(db: Session, org_id: str) -> Dict[str, float]:
    """
    Calculates the Placement Readiness Score using a weighted formula.

    Formula:
      Score = (Avg_ATS_Match × 0.6) + (Project_Completeness × 0.3) + (Interview_Participation × 0.1)

    Returns:
      {
        "readiness_score": 87.5,
        "avg_ats_match": 82.0,
        "project_completeness": 95.0,
        "interview_participation": 100.0
      }
    """
    users = db.query(User).filter_by(org_id=org_id, is_active=True, role="student").all()
    if not users:
        return {
            "readiness_score": 0.0,
            "avg_ats_match": 0.0,
            "project_completeness": 0.0,
            "interview_participation": 0.0,
        }

    total_match = 0.0
    project_count = 0
    interview_count = 0
    valid_sessions = 0

    for user in users:
        session = (
            db.query(AgentSession)
            .filter_by(user_id=user.id)
            .order_by(AgentSession.updated_at.desc())
            .first()
        )
        if not session:
            continue

        valid_sessions += 1

        # ATS Match
        match_pct = session.match_pct or 0.0
        total_match += match_pct

        # Project completeness (did they complete the project agent?)
        completed = session.completed_agents or []
        if "project" in completed:
            project_count += 1

        # Interview participation (did they complete the interview agent?)
        if "interview" in completed:
            interview_count += 1

    if valid_sessions == 0:
        return {
            "readiness_score": 0.0,
            "avg_ats_match": 0.0,
            "project_completeness": 0.0,
            "interview_participation": 0.0,
        }

    avg_ats_match = total_match / valid_sessions
    project_completeness = (project_count / valid_sessions) * 100
    interview_participation = (interview_count / valid_sessions) * 100

    # Weighted formula
    readiness_score = (
        (avg_ats_match * 0.6) + (project_completeness * 0.3) + (interview_participation * 0.1)
    )

    return {
        "readiness_score": round(readiness_score, 1),
        "avg_ats_match": round(avg_ats_match, 1),
        "project_completeness": round(project_completeness, 1),
        "interview_participation": round(interview_participation, 1),
    }


def generate_actionable_insight(
    readiness_score: float,
    top_missing_skills: List[Dict],
    dream_companies: List[str],
) -> str:
    """
    Generates a dynamic, actionable insight based on the readiness score and skill gaps.

    Example output:
      "Based on this score, your batch is a 92% match for Product-Based Companies
       (e.g., Google, Amazon) but needs improvement in System Design for Fintech roles."
    """
    if readiness_score >= 85:
        match_level = "excellent"
        company_type = "Product-Based Companies"
    elif readiness_score >= 70:
        match_level = "strong"
        company_type = "Service-Based Companies"
    elif readiness_score >= 50:
        match_level = "moderate"
        company_type = "Startups and Mid-Sized Firms"
    else:
        match_level = "developing"
        company_type = "Entry-Level Roles"

    # Extract top 3 missing skills
    top_gaps = [s["skill"] for s in top_missing_skills[:3]]
    gap_text = ", ".join(top_gaps) if top_gaps else "foundational skills"

    # Build company examples
    if dream_companies:
        company_examples = ", ".join(dream_companies[:3])
    else:
        company_examples = "Google, Amazon, Microsoft"

    insight = (
        f"Based on this score, your batch is a {match_level} match ({int(readiness_score)}%) "
        f"for {company_type} (e.g., {company_examples}). "
        f"Focus on improving {gap_text} to increase placement readiness."
    )

    return insight
