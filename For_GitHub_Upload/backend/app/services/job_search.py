"""
Job search service to find relevant job listings based on resume analysis.
"""
import requests
import json
import os
from typing import Dict, Any, List
from app.services.resume_analyzer import ResumeAnalyzerService


class JobSearchService:
    """Service for searching and matching relevant jobs to resumes."""
    
    def __init__(self):
        """Initialize the service."""
        self.analyzer = ResumeAnalyzerService()
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        
    def extract_job_keywords(self, resume: str) -> Dict[str, Any]:
        """Extract job titles, skills, and experience level from resume."""
        try:
            prompt = f"""Analyze this resume and extract job search keywords in JSON format.
                    
Resume:
{resume}

Return ONLY valid JSON (no markdown, no extra text) with this structure:
{{
    "job_titles": ["list of 3-5 relevant job titles"],
    "skills": ["list of 5-8 key technical skills"],
    "experience_level": "entry/mid/senior",
    "industries": ["list of relevant industries"],
    "search_query": "best single search query for job boards"
}}"""
            
            response = self.analyzer.ai_model._call_groq(prompt)
            
            # Parse JSON response
            try:
                data = json.loads(response)
                return data
            except json.JSONDecodeError:
                # If response isn't valid JSON, create default structure
                return {
                    "job_titles": ["Software Engineer", "Developer"],
                    "skills": ["Python", "JavaScript", "Full Stack"],
                    "experience_level": "mid",
                    "industries": ["Technology", "Software"],
                    "search_query": "software engineer"
                }
        except Exception as e:
            print(f"Error extracting keywords: {str(e)}")
            return {
                "job_titles": ["Software Engineer"],
                "skills": [],
                "experience_level": "mid",
                "industries": ["Technology"],
                "search_query": "software engineer"
            }
    
    def search_jobs_jsearch(self, keywords: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for jobs using JSearch API from RapidAPI."""
        if not self.rapidapi_key:
            return self._generate_mock_jobs(keywords)
        
        try:
            search_query = keywords.get("search_query", "Software Engineer")
            
            url = "https://jsearch.p.rapidapi.com/search"
            
            querystring = {
                "query": search_query,
                "page": "1",
                "num_pages": "1"
            }
            
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get("data", [])
            
            # Format and enhance jobs
            formatted_jobs = []
            for job in jobs[:10]:  # Limit to 10 jobs
                formatted_jobs.append({
                    "id": job.get("job_id"),
                    "title": job.get("job_title"),
                    "company": job.get("employer_name"),
                    "location": job.get("job_location", "Remote"),
                    "type": job.get("job_employment_type", "Full-time"),
                    "description": job.get("job_description", "")[:500],  # First 500 chars
                    "salary": job.get("job_salary_currency", "") + " " + str(job.get("job_salary_max", "") or "Negotiable"),
                    "apply_url": job.get("job_apply_link"),
                    "posted_date": job.get("job_posted_at_datetime_utc", ""),
                    "match_score": self._calculate_match_score(job, keywords)
                })
            
            return sorted(formatted_jobs, key=lambda x: x["match_score"], reverse=True)
        
        except Exception as e:
            print(f"Error searching jobs: {str(e)}")
            return self._generate_mock_jobs(keywords)
    
    def _calculate_match_score(self, job: Dict, keywords: Dict) -> float:
        """Calculate relevance score between job and resume keywords."""
        score = 0.5  # Base score
        
        job_title = (job.get("job_title", "") + " " + job.get("job_description", "")).lower()
        
        # Check job title matches
        for title in keywords.get("job_titles", []):
            if title.lower() in job_title:
                score += 0.15
        
        # Check skill matches
        for skill in keywords.get("skills", []):
            if skill.lower() in job_title:
                score += 0.05
        
        # Check industry matches
        for industry in keywords.get("industries", []):
            if industry.lower() in job_title:
                score += 0.10
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _generate_mock_jobs(self, keywords: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mock job listings when API is unavailable."""
        job_titles = keywords.get("job_titles", ["Software Engineer"])
        skills = keywords.get("skills", [])
        companies = [
            "TechCorp Solutions", "Innovation Labs", "Digital Ventures",
            "CloudFirst Inc", "DataFlow Systems", "DevOps Hub",
            "StartUp AI", "Enterprise Tech"
        ]
        locations = ["Remote", "Bangalore", "Delhi", "Hyderabad", "San Francisco", "New York"]
        
        jobs = []
        for i, title in enumerate(job_titles[:5]):
            jobs.append({
                "id": f"job_{i}",
                "title": title,
                "company": companies[i % len(companies)],
                "location": locations[i % len(locations)],
                "type": "Full-time",
                "description": f"We are looking for a talented {title} with expertise in {', '.join(skills[:3])}. "
                              f"Join our growing team and make an impact in the tech industry. "
                              f"Responsibilities include developing scalable solutions, collaborating with teams, "
                              f"and driving innovation.",
                "salary": "₹8-15 LPA",
                "apply_url": f"https://www.linkedin.com/jobs/search/?keywords={title.replace(' ', '%20')}",
                "posted_date": "2 days ago",
                "match_score": 0.85 - (i * 0.05)
            })
        
        return jobs
    
    def get_matching_jobs(self, resume: str) -> Dict[str, Any]:
        """Main method to get jobs matching the resume."""
        try:
            # Extract keywords from resume
            keywords = self.extract_job_keywords(resume)
            
            # Search for jobs
            jobs = self.search_jobs_jsearch(keywords)
            
            return {
                "success": True,
                "keywords": keywords,
                "jobs": jobs,
                "total": len(jobs)
            }
        
        except Exception as e:
            print(f"Error getting matching jobs: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "jobs": [],
                "total": 0
            }
