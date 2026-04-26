"""
Input validation utilities.
"""
from typing import Tuple


class InputValidator:
    """Validate user inputs."""
    
    MIN_RESUME_LENGTH = 50
    MIN_JOB_DESC_LENGTH = 30
    MAX_RESUME_LENGTH = 50000
    MAX_JOB_DESC_LENGTH = 10000
    
    @staticmethod
    def validate_resume(resume: str) -> Tuple[bool, str]:
        """
        Validate resume input.
        
        Args:
            resume: Resume text
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not resume:
            return False, "Resume cannot be empty"
        
        resume = resume.strip()
        
        if len(resume) < InputValidator.MIN_RESUME_LENGTH:
            return False, f"Resume must be at least {InputValidator.MIN_RESUME_LENGTH} characters"
        
        if len(resume) > InputValidator.MAX_RESUME_LENGTH:
            return False, f"Resume cannot exceed {InputValidator.MAX_RESUME_LENGTH} characters"
        
        return True, ""
    
    @staticmethod
    def validate_job_description(job_desc: str) -> Tuple[bool, str]:
        """
        Validate job description input.
        
        Args:
            job_desc: Job description text
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not job_desc:
            return False, "Job description cannot be empty"
        
        job_desc = job_desc.strip()
        
        if len(job_desc) < InputValidator.MIN_JOB_DESC_LENGTH:
            return False, f"Job description must be at least {InputValidator.MIN_JOB_DESC_LENGTH} characters"
        
        if len(job_desc) > InputValidator.MAX_JOB_DESC_LENGTH:
            return False, f"Job description cannot exceed {InputValidator.MAX_JOB_DESC_LENGTH} characters"
        
        return True, ""
    
    @staticmethod
    def validate_both(resume: str, job_desc: str) -> Tuple[bool, str]:
        """
        Validate both resume and job description.
        
        Args:
            resume: Resume text
            job_desc: Job description text
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, error = InputValidator.validate_resume(resume)
        if not is_valid:
            return False, error
        
        is_valid, error = InputValidator.validate_job_description(job_desc)
        if not is_valid:
            return False, error
        
        return True, ""
