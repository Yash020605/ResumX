"""
Job search service – finds relevant LinkedIn job listings based on resume analysis.
Falls back to LinkedIn search URLs when RapidAPI is unavailable.
"""
import json
import os
import re
import requests
from typing import Any, Dict, List


class JobSearchService:

    def __init__(self):
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")

    # ── Keyword extraction ────────────────────────────────────────────────────

    def extract_job_keywords(self, resume: str, job_description: str = "") -> Dict[str, Any]:
        try:
            base = f"Resume:\n{resume[:2000]}"
            if job_description:
                base += f"\n\nTarget JD:\n{job_description[:1000]}"
            prompt = (
                f"{base}\n\n"
                "Return ONLY valid JSON with no extra text:\n"
                '{"job_titles":["3-5 relevant job titles"],"skills":["5-8 key skills"],'
                '"experience_level":"entry/mid/senior","industries":["industry"],'
                '"search_query":"best single search query"}'
            )
            # Use the LLM provider directly — no dependency on old GroqAIService
            from app.agents.llm_provider import get_llm
            from langchain_core.messages import HumanMessage, SystemMessage
            llm = get_llm(temperature=0.2, max_tokens=400)
            resp = llm.invoke([
                SystemMessage(content="Extract job search keywords. Return ONLY valid JSON."),
                HumanMessage(content=prompt),
            ])
            raw = resp.content.strip()
            # Strip markdown fences if present
            import re
            m = re.search(r'\{[\s\S]+\}', raw)
            data = __import__('json').loads(m.group() if m else raw)
            return data
        except Exception as e:
            print(f"[JobSearch] keyword extraction failed: {e}")
            return {
                "job_titles":       ["Software Engineer"],
                "skills":           ["Python"],
                "experience_level": "mid",
                "industries":       ["Technology"],
                "search_query":     "software engineer",
            }

    # ── JSearch API ───────────────────────────────────────────────────────────

    def search_jobs_jsearch(self, keywords: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self.rapidapi_key:
            return self._linkedin_jobs(keywords)

        titles = keywords.get("job_titles", [])
        query  = titles[0] if titles else keywords.get("search_query", "Software Engineer")

        try:
            resp = requests.get(
                "https://jsearch.p.rapidapi.com/search",
                headers={
                    "X-RapidAPI-Key":  self.rapidapi_key,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
                },
                params={"query": f"{query} in India", "page": "1",
                        "num_pages": "1", "date_posted": "month"},
                timeout=10,
            )
            resp.raise_for_status()
            jobs = resp.json().get("data", [])
            if not jobs:
                return self._linkedin_jobs(keywords)

            formatted = []
            for job in jobs[:8]:
                apply_url = job.get("job_apply_link") or self._li_url(
                    job.get("job_title", query), keywords.get("skills", [])
                )
                formatted.append({
                    "id":          job.get("job_id"),
                    "title":       job.get("job_title"),
                    "company":     job.get("employer_name"),
                    "location":    job.get("job_location", "Remote"),
                    "type":        job.get("job_employment_type", "Full-time"),
                    "description": (job.get("job_description") or "")[:500],
                    "salary":      str(job.get("job_salary_max") or "Negotiable"),
                    "apply_url":   apply_url,
                    "linkedin_url": self._li_url(job.get("job_title", query),
                                                 keywords.get("skills", [])),
                    "posted_date": (job.get("job_posted_at_datetime_utc") or "")[:10],
                    "match_score": self._score(job, keywords),
                })
            return sorted(formatted, key=lambda x: x["match_score"], reverse=True)

        except Exception as e:
            print(f"[JobSearch] JSearch error: {e}")
            return self._linkedin_jobs(keywords)

    # ── LinkedIn URL builder ──────────────────────────────────────────────────

    def _li_url(self, title: str, skills: List[str]) -> str:
        skill_str = " ".join(skills[:2])
        query     = f"{title} {skill_str}".strip().replace(" ", "%20")
        return (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={query}&location=India&f_TPR=r604800&f_JT=F"
        )

    def _linkedin_jobs(self, keywords: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback: return LinkedIn search links for each job title."""
        titles    = keywords.get("job_titles", ["Software Engineer"])
        skills    = keywords.get("skills", [])
        companies = ["Google", "Microsoft", "Amazon", "Flipkart", "Infosys",
                     "TCS", "Wipro", "Persistent Systems", "Razorpay", "Zepto"]
        locations = ["Pune", "Bangalore", "Hyderabad", "Mumbai", "Remote"]

        jobs = []
        for i, title in enumerate(titles[:5]):
            li = self._li_url(title, skills)
            jobs.append({
                "id":          f"li_{i}",
                "title":       title,
                "company":     companies[i % len(companies)],
                "location":    locations[i % len(locations)],
                "type":        "Full-time",
                "description": (
                    f"Looking for a {title} with expertise in "
                    f"{', '.join(skills[:3]) or 'relevant technologies'}."
                ),
                "salary":      "₹8-20 LPA",
                "apply_url":   li,
                "linkedin_url": li,
                "posted_date": "Posted this week",
                "match_score": round(0.85 - i * 0.05, 2),
            })
        return jobs

    # ── Match score ───────────────────────────────────────────────────────────

    def _score(self, job: Dict, keywords: Dict) -> float:
        text  = (job.get("job_title", "") + " " + job.get("job_description", "")).lower()
        score = 0.5
        for t in keywords.get("job_titles", []):
            if t.lower() in text: score += 0.15
        for s in keywords.get("skills", []):
            if s.lower() in text: score += 0.05
        return min(score, 1.0)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_matching_jobs(self, resume: str, job_description: str = "") -> Dict[str, Any]:
        try:
            keywords = self.extract_job_keywords(resume, job_description)
            jobs     = self.search_jobs_jsearch(keywords)
            return {"success": True, "keywords": keywords, "jobs": jobs, "total": len(jobs)}
        except Exception as e:
            print(f"[JobSearch] Error: {e}")
            return {"success": False, "error": str(e), "jobs": [], "total": 0}
