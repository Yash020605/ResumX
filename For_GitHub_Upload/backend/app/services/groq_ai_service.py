"""
Groq AI Service for Resume Analysis
Uses Groq API instead of local transformers for AI-powered resume analysis.
"""
import os
import json
import requests
from typing import Dict, Any, List


class GroqAIService:
    """AI service using Groq API for resume analysis."""

    def __init__(self):
        """Initialize the Groq AI service."""
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")

        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = "llama-3.3-70b-versatile"  # Updated to current Groq model

    def _call_groq(self, prompt: str, max_tokens: int = 2000) -> str:
        """Make a call to Groq API with the given prompt."""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant specializing in resume analysis and career guidance. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise Exception(f"Groq API call failed: {str(e)}")

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from Groq, handling potential formatting issues."""
        try:
            # Try direct JSON parsing
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                if json_end > json_start:
                    json_content = response[json_start:json_end].strip()
                    return json.loads(json_content)

            # Try to find JSON-like content with better error handling
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_content = response[start_idx:end_idx]
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    # Try to fix common JSON issues
                    json_content = json_content.replace("'", '"')  # Replace single quotes
                    json_content = json_content.replace('\n', ' ')  # Remove newlines
                    json_content = json_content.replace('\r', ' ')  # Remove carriage returns
                    return json.loads(json_content)

            raise ValueError(f"Could not parse JSON from response: {response[:200]}...")

    def analyze_resume_match(self, resume: str, job_description: str) -> Dict[str, Any]:
        """
        Analyze how well a resume matches a job description using Groq API.

        Args:
            resume: Full resume text
            job_description: Job description text

        Returns:
            Dictionary with analysis results
        """
        prompt = f"""
Analyze how well this resume matches this job description. Provide a detailed analysis in the following JSON format:

{{
    "match_percentage": <number between 0-100>,
    "matching_skills": [<list of skills that appear in both resume and job description>],
    "missing_skills": [<list of important skills from job description not found in resume>],
    "skill_gaps": [
        {{
            "skill": "<skill name>",
            "importance": "<high/medium/low>"
        }}
    ],
    "feedback": "<detailed feedback on the match quality>",
    "improvements": [<list of specific improvement suggestions>],
    "career_fields": [<list of relevant career fields based on resume skills>],
    "key_strengths": [<top 3 strengths from resume>],
    "summary": "<brief summary of the analysis>"
}}

Resume:
{resume}

Job Description:
{job_description}

Respond with ONLY valid JSON, no additional text.
"""

        try:
            response = self._call_groq(prompt, max_tokens=1500)
            result = self._parse_json_response(response)

            # Ensure all required keys are present with defaults if missing
            required_keys = [
                "match_percentage", "matching_skills", "missing_skills",
                "skill_gaps", "feedback", "improvements", "career_fields",
                "key_strengths", "summary"
            ]

            for key in required_keys:
                if key not in result:
                    if key in ["matching_skills", "missing_skills", "improvements", "career_fields", "key_strengths"]:
                        result[key] = []
                    elif key == "skill_gaps":
                        result[key] = []
                    elif key == "match_percentage":
                        result[key] = 50
                    else:
                        result[key] = f"Analysis for {key} not available"

            return result

        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}"
            }

    def generate_improved_resume(
        self,
        original_resume: str,
        job_description: str,
        improvements: list
    ) -> Dict[str, Any]:
        """
        Generate an improved version of the resume tailored to job description.

        Args:
            original_resume: Original resume text
            job_description: Target job description
            improvements: List of improvements to implement

        Returns:
            Dictionary with improved resume and metadata
        """
        prompt = f"""
Based on the job description and the requested improvements, create an improved version of the resume. Focus on incorporating the key skills and requirements from the job description while implementing the suggested improvements.

Improvements to implement: {', '.join(improvements)}

Provide your response in the following JSON format:
{{
    "success": true,
    "improved_resume": "<the complete improved resume text>",
    "status": "<brief description of changes made>"
}}

Original Resume:
{original_resume}

Job Description:
{job_description}

Respond with ONLY valid JSON, no additional text.
"""

        try:
            response = self._call_groq(prompt, max_tokens=2000)
            result = self._parse_json_response(response)

            # Ensure required keys
            if "success" not in result:
                result["success"] = True
            if "improved_resume" not in result:
                result["improved_resume"] = original_resume
            if "status" not in result:
                result["status"] = "Resume updated with job-specific improvements"

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Resume improvement failed: {str(e)}"
            }

    def get_career_fields(self, resume: str) -> Dict[str, Any]:
        """
        Suggest career fields and roles based on resume using Groq API.

        Args:
            resume: Resume text

        Returns:
            Dictionary with career suggestions
        """
        prompt = f"""
Based on the skills and experience in this resume, suggest appropriate career fields, job titles, and related information. Provide detailed career guidance.

Resume:
{resume}

Provide your response in the following JSON format:
{{
    "career_fields": [
        {{
            "field": "<career field name>",
            "explanation": "<why this field suits the candidate>"
        }}
    ],
    "job_titles": [<list of relevant job titles>],
    "industries": [<list of relevant industries>],
    "growth_opportunities": [<list of potential next career steps>],
    "recommended_skills": [<additional skills to develop>],
    "certifications": [<recommended certifications>],
    "summary": "<overall career summary based on resume>"
}}

Respond with ONLY valid JSON, no additional text.
"""

        try:
            response = self._call_groq(prompt, max_tokens=1500)
            result = self._parse_json_response(response)

            # Ensure required keys with defaults
            required_keys = [
                "career_fields", "job_titles", "industries", "growth_opportunities",
                "recommended_skills", "certifications", "summary"
            ]

            for key in required_keys:
                if key not in result:
                    if key in ["career_fields", "job_titles", "industries", "growth_opportunities", "recommended_skills", "certifications"]:
                        result[key] = []
                    else:
                        result[key] = f"Career analysis for {key} not available"

            return result

        except Exception as e:
            return {
                "error": f"Career analysis failed: {str(e)}"
            }

    def generate_interview_prep(
        self,
        resume: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Generate interview preparation guide using Groq API.

        Args:
            resume: Resume text
            job_description: Job description text

        Returns:
            Dictionary with interview preparation content
        """
        prompt = f"""
Create a comprehensive interview preparation guide based on the resume and job description. Include probable questions, focus areas, and preparation tips.

Resume:
{resume}

Job Description:
{job_description}

Provide your response in the following JSON format:
{{
    "probable_questions": [<list of likely interview questions>],
    "focus_areas": [<key areas to prepare for>],
    "expected_answers": {{
        "<question>": "<expected answer guidance>",
        "<question>": "<expected answer guidance>"
    }},
    "follow_up_questions": [<potential follow-up questions>],
    "common_mistakes": [<common mistakes to avoid>],
    "strengths_to_highlight": [<key strengths to emphasize>],
    "prep_resources": [<recommended preparation resources>],
    "tips": [<specific preparation tips>]
}}

Respond with ONLY valid JSON, no additional text.
"""

        try:
            response = self._call_groq(prompt, max_tokens=1500)
            result = self._parse_json_response(response)

            # Ensure required keys with defaults
            required_keys = [
                "probable_questions", "focus_areas", "expected_answers",
                "follow_up_questions", "common_mistakes", "strengths_to_highlight",
                "prep_resources"
            ]

            for key in required_keys:
                if key not in result:
                    if key in ["probable_questions", "focus_areas", "follow_up_questions", "common_mistakes", "strengths_to_highlight", "prep_resources"]:
                        result[key] = []
                    elif key == "expected_answers":
                        result[key] = {}
                    else:
                        result[key] = f"Interview prep for {key} not available"

            # Add tips if not present
            if "tips" not in result:
                result["tips"] = ["Practice common technical questions", "Prepare examples from your experience", "Research the company thoroughly"]

            return result

        except Exception as e:
            return {
                "error": f"Interview prep generation failed: {str(e)}"
            }
