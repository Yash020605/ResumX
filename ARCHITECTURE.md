version: 1.0.0
title: "ResumeX - AI Career Coach"

overview: |
  A comprehensive, production-ready AI-powered resume analysis and optimization platform.
  
  The application uses Claude AI to provide intelligent, fact-based analysis of resumes
  against job descriptions, with features for resume optimization, career guidance, and
  interview preparation.

architecture: |
  ┌─────────────────────┐
  │  React Frontend     │ (Port 3000)
  │  - Vite + Tailwind  │
  │  - Zustand Store    │
  │  - Axios HTTP       │
  └──────────┬──────────┘
             │
             │ REST API (JSON)
             │
  ┌──────────▼──────────┐
  │ Flask Backend       │ (Port 5000)
  │ - Python 3.11      │
  │ - Claude AI        │
  │ - PDF Processing   │
  │ - Structured Logs   │
  └─────────────────────┘

technology_stack:
  frontend:
    - React 18.2
    - Vite 5.0
    - Tailwind CSS 3
    - Zustand (State Management)
    - Axios (HTTP Client)
    - Lucide React (Icons)
    - React Markdown
  
  backend:
    - Flask 3.0
    - Flask-CORS
    - Anthropic Claude 3.5 Sonnet
    - PDFPlumber (PDF Extraction)
    - Python 3.11
    - Gunicorn (Production Server)
  
  deployment:
    - Docker & Docker Compose
    - Multi-container setup
    - Health checks configured

features:
  core:
    - Resume-Job Description Matching Analysis
    - Match Percentage Scoring (0-100%)
    - Skill Gap Analysis
    - Key Strengths Identification
    - Actionable Improvement Suggestions
  
  optimization:
    - AI-Enhanced Resume Generation
    - ATS-Friendly Formatting
    - Keyword Optimization
    - Authentic Rephrasing (no false claims)
  
  career_guidance:
    - Career Field Suggestions (5-7 fields)
    - Job Title Recommendations (10-15 titles)
    - Industry Analysis
    - Growth Opportunity Identification
    - Skill Development Recommendations
    - Certification Suggestions
  
  interview_prep:
    - Probable Interview Questions (8-12)
    - Focus Area Identification
    - Sample Answers Based on Resume
    - Follow-up Question Preparation
    - Common Mistakes to Avoid
    - Strengths to Emphasize
  
  ui_features:
    - PDF Resume Upload Support
    - Text Resume Input
    - Real-time Analysis
    - Tabbed Results Display
    - Copy & Download Functions
    - Responsive Design
    - Beautiful UI with Gradients

hallucination_prevention:
  - Only analyzes explicitly present resume information
  - Requires evidence for all claims
  - Avoids speculation about qualifications
  - Fact-based, citation-aware analysis
  - Clear uncertainty indicators when applicable
  - Structured JSON validation
  - Input validation and sanitization

api_endpoints:
  /api/health:
    method: GET
    description: Health check endpoint
  
  /api/analyze:
    method: POST
    description: Analyze resume against job description
    body:
      resume: string (required)
      job_description: string (required)
  
  /api/improve-resume:
    method: POST
    description: Generate improved resume version
    body:
      resume: string (required)
      job_description: string (required)
      improvements: array (required)
  
  /api/career-fields:
    method: POST
    description: Get career field suggestions
    body:
      resume: string (required)
  
  /api/interview-prep:
    method: POST
    description: Generate interview preparation guide
    body:
      resume: string (required)
      job_description: string (required)
  
  /api/upload-pdf:
    method: POST
    description: Upload and extract text from PDF
    body: multipart/form-data with 'file' field

response_schema:
  analysis:
    match_percentage: integer (0-100)
    matching_skills: array of strings
    missing_skills: array of strings
    skill_gaps: array of objects with skill and importance
    feedback: string (detailed analysis)
    improvements: array of strings
    career_fields: array of strings
    key_strengths: array of strings
    summary: string
  
  resume_improvement:
    success: boolean
    improved_resume: string
    status: string
  
  career_fields:
    career_fields: array of objects
    job_titles: array of strings
    industries: array of strings
    growth_opportunities: array of strings
    recommended_skills: array of strings
    certifications: array of strings
    summary: string
  
  interview_prep:
    probable_questions: array of strings
    focus_areas: array of strings
    expected_answers: object (question -> answer)
    follow_up_questions: array of strings
    common_mistakes: array of strings
    strengths_to_highlight: array of strings
    prep_resources: array of strings
