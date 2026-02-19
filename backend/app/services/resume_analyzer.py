"""
Resume analysis service using Groq AI API.
Handles all resume-related AI operations with Groq API.
"""
import os
from typing import Dict, Any, Optional
from app.services.groq_ai_service import GroqAIService
from app.utils.parsers import ResponseParser


class ResumeAnalyzerService:
    """Service for analyzing resumes using Groq AI API."""

    def __init__(self):
        """Initialize the service with Groq AI service."""
        try:
            self.ai_model = GroqAIService()
            print("Groq AI service initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Groq AI service: {e}")
            raise

    def analyze_resume_match(self, resume: str, job_description: str) -> Dict[str, Any]:
        """
        Analyze how well a resume matches a job description.

        Args:
            resume: Full resume text
            job_description: Job description text

        Returns:
            Dictionary with analysis results
        """
        return self.ai_model.analyze_resume_match(resume, job_description)

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
        return self.ai_model.generate_improved_resume(original_resume, job_description, improvements)

    def get_career_fields(self, resume: str) -> Dict[str, Any]:
        """
        Suggest career fields and roles based on resume.

        Args:
            resume: Resume text

        Returns:
            Dictionary with career suggestions
        """
        return self.ai_model.get_career_fields(resume)

    def generate_interview_prep(
        self,
        resume: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Generate interview preparation guide with probable questions.

        Args:
            resume: Resume text
            job_description: Job description text

        Returns:
            Dictionary with interview preparation content
        """
        return self.ai_model.generate_interview_prep(resume, job_description)
