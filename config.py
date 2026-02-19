"""
AI Resume Analyzer - Project-wide configuration
"""

# API Configuration
API_VERSION = "1.0.0"
API_BASE_URL = "http://localhost:5000"
API_TIMEOUT = 30  # seconds

# Frontend Configuration
FRONTEND_PORT = 3000
FRONTEND_BASE_URL = "http://localhost:3000"

# Backend Configuration
BACKEND_PORT = 5000
BACKEND_HOST = "0.0.0.0"

# File Upload Configuration
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx'}

# AI Model Configuration
AI_MODEL = "claude-3-5-sonnet-20241022"
AI_MAX_TOKENS = {
    "analysis": 2000,
    "resume_improvement": 3000,
    "career_guidance": 1500,
    "interview_prep": 2500,
}

# Resume Validation
MIN_RESUME_LENGTH = 50
MAX_RESUME_LENGTH = 50000
MIN_JOB_DESC_LENGTH = 30
MAX_JOB_DESC_LENGTH = 10000

# Hallucination Prevention
STRICT_ANALYSIS = True  # Enable strict, fact-based analysis
REQUIRE_EVIDENCE = True  # Require evidence from resume for claims
