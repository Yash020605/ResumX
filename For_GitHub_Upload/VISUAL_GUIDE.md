# AI Resume Analyzer - Visual Guide

## Application Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE (React)                       │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │  Resume Input    │  │  Job Description │  │  Action Buttons │  │
│  │  • Text input    │  │  • Paste content │  │  • Analyze      │  │
│  │  • PDF upload    │  │  • Validation    │  │  • Improve      │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           Results Display (Tabbed Interface)                 │  │
│  │  • Analysis | Improved | Career | Interview                  │  │
│  │                                                               │  │
│  │  Analysis Results:                                           │  │
│  │  - Match Score (0-100%)                                     │  │
│  │  - Matching Skills                                          │  │
│  │  - Missing Skills                                           │  │
│  │  - Improvements                                             │  │
│  │  - Career Suggestions                                       │  │
│  │                                                               │  │
│  │  Improved Resume:                                            │  │
│  │  - Optimized content                                        │  │
│  │  - Copy & Download buttons                                  │  │
│  │                                                               │  │
│  │  Career Fields:                                              │  │
│  │  - 5-7 Career paths                                         │  │
│  │  - Job titles                                               │  │
│  │  - Industries                                               │  │
│  │  - Skills to develop                                        │  │
│  │                                                               │  │
│  │  Interview Prep:                                             │  │
│  │  - Probable questions                                       │  │
│  │  - Sample answers                                           │  │
│  │  - Focus areas                                              │  │
│  │  - Common mistakes                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      API LAYER (REST/JSON)                           │
│                                                                       │
│  POST /api/analyze                                                   │
│  POST /api/improve-resume                                            │
│  POST /api/career-fields                                             │
│  POST /api/interview-prep                                            │
│  POST /api/upload-pdf                                                │
│  GET  /api/health                                                    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (Flask + Python)                        │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Input Validation & Parsing                       │  │
│  │  • Length validation                                          │  │
│  │  • PDF extraction (PDFPlumber)                               │  │
│  │  • JSON schema validation                                    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                 ↓                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │          Resume Analysis Service                              │  │
│  │                                                               │  │
│  │  1. analyze_resume_match()                                   │  │
│  │     - Match scoring                                          │  │
│  │     - Skill extraction                                       │  │
│  │     - Gap analysis                                           │  │
│  │                                                               │  │
│  │  2. generate_improved_resume()                               │  │
│  │     - Rewrite with improvements                              │  │
│  │     - ATS optimization                                       │  │
│  │     - Maintain authenticity                                  │  │
│  │                                                               │  │
│  │  3. get_career_fields()                                      │  │
│  │     - Career suggestions                                     │  │
│  │     - Job titles                                             │  │
│  │     - Industry analysis                                      │  │
│  │                                                               │  │
│  │  4. generate_interview_prep()                                │  │
│  │     - Question generation                                    │  │
│  │     - Answer samples                                         │  │
│  │     - Focus areas                                            │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                 ↓                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │          Claude 3.5 Sonnet AI (Anthropic API)                │  │
│  │                                                               │  │
│  │  • Factual analysis (evidence-based)                         │  │
│  │  • Structured prompting (JSON responses)                     │  │
│  │  • Hallucination prevention                                  │  │
│  │  • Professional writing                                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                 ↓                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │          Response Parsing & Validation                       │  │
│  │  • JSON extraction                                           │  │
│  │  • Error handling                                            │  │
│  │  • Response formatting                                       │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
                    Response sent to Frontend
```

## User Journey

```
START
  ↓
[Upload Resume or Paste Text]
  ↓
[Paste Job Description]
  ↓
[Click "Analyze Resume"]
  ↓
[LOADING... Processing with Claude AI]
  ↓
[View Analysis Results]
  ├─→ Match Score (0-100%)
  ├─→ Matching Skills
  ├─→ Missing Skills
  ├─→ Improvements
  └─→ Career Suggestions
  ↓
[Choose Next Action]
  ├─→ [Improve Resume] → View optimized content → Download
  ├─→ [Career Fields] → Explore 5-7 career paths
  ├─→ [Interview Prep] → Practice questions & answers
  └─→ [Analyze Another] → Start over
  ↓
END
```

## Component Hierarchy

```
App
├── HomePage
│   ├── Header
│   ├── InputSection
│   │   ├── ResumeInput
│   │   │   ├── TextArea
│   │   │   └── PDFUploader
│   │   └── JobDescriptionInput
│   │       └── TextArea
│   ├── ActionButtons
│   │   ├── AnalyzeButton
│   │   ├── ImproveButton
│   │   ├── CareerButton
│   │   └── InterviewButton
│   ├── TabNavigation
│   │   ├── AnalysisTab
│   │   ├── ImprovedTab
│   │   ├── CareerTab
│   │   └── InterviewTab
│   └── ResultsSection
│       ├── AnalysisResults
│       │   ├── MatchScore
│       │   ├── SkillsList
│       │   ├── GapAnalysis
│       │   └── Improvements
│       ├── ImprovedResumeDisplay
│       │   ├── ResumeContent
│       │   ├── CopyButton
│       │   └── DownloadButton
│       ├── CareerFieldsDisplay
│       │   ├── CareerFields
│       │   ├── JobTitles
│       │   └── Industries
│       └── InterviewPrepDisplay
│           ├── Questions
│           ├── Answers
│           └── FocusAreas
└── LoadingSpinner / ErrorMessage / SuccessMessage
```

## API Response Structure

### Analysis Response
```json
{
  "success": true,
  "analysis": {
    "match_percentage": 75,
    "matching_skills": ["Python", "React", "REST API"],
    "missing_skills": ["Docker", "AWS"],
    "skill_gaps": [
      {"skill": "Docker", "importance": "high"},
      {"skill": "AWS", "importance": "medium"}
    ],
    "feedback": "Your resume is well-structured...",
    "improvements": [
      "Add quantifiable achievements",
      "Highlight leadership experience"
    ],
    "career_fields": ["Backend Engineer", "Full Stack Developer"],
    "key_strengths": ["Problem solving", "Python expertise"],
    "summary": "Good fit for this role..."
  }
}
```

### Improved Resume Response
```json
{
  "success": true,
  "improved_resume": "Improved resume text...",
  "status": "Resume successfully improved"
}
```

### Career Fields Response
```json
{
  "success": true,
  "career_data": {
    "career_fields": ["Data Science", "Machine Learning Engineer"],
    "job_titles": ["Data Scientist", "ML Engineer"],
    "industries": ["Tech", "Finance", "Healthcare"],
    "growth_opportunities": ["Lead data scientist", "Research scientist"],
    "recommended_skills": ["TensorFlow", "SQL"],
    "certifications": ["Google Cloud Architect"],
    "summary": "Strong background in data..."
  }
}
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Docker Host                        │
│                                                         │
│  ┌───────────────────┐  ┌──────────────────────────┐  │
│  │  Frontend         │  │  Backend Container       │  │
│  │  Container        │  │                          │  │
│  │                   │  │  Python 3.11             │  │
│  │  Node 18-alpine   │  │  Flask 3.0               │  │
│  │  npm run dev      │  │  Gunicorn 4 workers      │  │
│  │  Port: 3000       │  │  Port: 5000              │  │
│  │                   │  │  Healthcheck enabled     │  │
│  └───────────────────┘  └──────────────────────────┘  │
│          ↓                          ↓                   │
│    Docker network (resume-analyzer-network)            │
│          ↑                          ↑                   │
│  ┌─────────────────────────────────────────┐          │
│  │      Exposed Ports                      │          │
│  │  3000 → Frontend                        │          │
│  │  5000 → Backend                         │          │
│  └─────────────────────────────────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↓
  Docker Compose Controls
  - build
  - up/down
  - logs
  - scale
```

## Data Flow Example

```
User Input:
{
  "resume": "5+ years Python developer with React expertise...",
  "jobDescription": "Seeking Full Stack Developer with Python..."
}
       ↓
  Validation
  • Resume length check
  • Job desc length check
  • Input sanitization
       ↓
  API Request
  POST /api/analyze
       ↓
  Flask Route Handler
  • Receive JSON
  • Call service
       ↓
  ResumeAnalyzerService
  • Format prompt with evidence
  • Call Claude API
  • Parse response
       ↓
  Claude AI
  • Analyze resume against job
  • Generate JSON response
  • Ensure facts only
       ↓
  Response Parser
  • Extract JSON
  • Validate structure
  • Format for frontend
       ↓
  API Response
  {
    "success": true,
    "analysis": {...}
  }
       ↓
  Frontend Display
  • Show match score
  • Display skills
  • Render improvements
  • Update state
       ↓
  User sees results
  • Analyzes recommendations
  • Decides next action
  • Clicks improve, career, or interview button
```

This provides a comprehensive visual overview of how the application works!
