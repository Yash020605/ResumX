# AI Resume Analyzer - Complete Setup Guide

A production-ready, full-stack AI-powered resume analysis application with React frontend and Python backend using free/open-source AI providers (Groq or Ollama).

## 🚀 Features

### Core Analysis
- **Resume-Job Matching**: Detailed analysis of how well your resume matches job requirements
- **Match Scoring**: Quantified score (0-100%) with visual representation
- **Skill Analysis**: Identify matching skills and critical gaps
- **Gap Analysis**: Missing skills with importance levels
- **Key Strengths**: Automatic identification of top strengths

### Resume Optimization
- **AI-Enhanced Resume**: Generate improved resume tailored to job description
- **Authentic Rephrasing**: Maintains truthfulness, no false claims added
- **ATS-Friendly**: Optimized for Applicant Tracking Systems
- **Keyword Integration**: Natural inclusion of job-relevant keywords

### Career Guidance
- **Career Fields**: Discover 5-7 career paths you qualify for
- **Job Titles**: Get 10-15 specific job titles to search for
- **Industry Insights**: See which industries value your skills
- **Growth Paths**: Identify career growth opportunities
- **Skill Development**: Recommendations for skill improvement
- **Certifications**: Relevant certifications to pursue

### Interview Preparation
- **Probable Questions**: 8-12 likely interview questions
- **Sample Answers**: Based on your resume and job requirements
- **Focus Areas**: Key technical/soft skills to prepare
- **Follow-ups**: Common follow-up questions
- **Mistakes to Avoid**: Common interview pitfalls
- **Strengths Highlighting**: How to best present yourself

## 📋 System Requirements

- **Node.js**: 18.x or higher
- **Python**: 3.11 or higher
- **Docker** (optional): For containerized deployment
- **AI Provider**: Choose Groq (free, cloud) or Ollama (free, local)

## 🔧 Installation & Setup

### Option A: Using Groq (Recommended - Fastest Setup)

**Groq is free, instant setup, no credit card required.**

#### 1. Clone and Navigate

```bash
cd c:\Users\Yash\Desktop\Intership\TechGeek\Projects\AIResumeAnalyzer
```

#### 2. Get Your Groq API Key

1. Go to [Groq Console](https://console.groq.com)
2. Sign up (1 minute, no credit card)
3. Copy your API key from the console

#### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create .env file (copy from .env.example)
copy .env.example .env

# Edit .env and update:
# AI_PROVIDER=groq
# GROQ_API_KEY=your_groq_key_here

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
python wsgi.py
```

Backend will be available at: `http://localhost:5000`

#### 4. Frontend Setup

```bash
# Navigate to frontend directory (in new terminal)
cd frontend

# Create .env file
copy .env.example .env

# Install dependencies
npm install

# Start development server
npm run dev
```

Application will be available at: `http://localhost:5173`

---

### Option B: Using Ollama (Completely Free & Local)

**Ollama runs everything locally. No API keys, no internet required after setup.**

#### 1. Installation & Download

```bash
# Install Ollama from https://ollama.ai
# Then pull the Mistral model:
ollama pull mistral

# Start Ollama server (keep this running)
ollama serve
```

You should see: `Ollama running at http://localhost:11434`

#### 2. Backend Setup

```bash
cd backend

# Create .env file
copy .env.example .env

# Edit .env and set:
# AI_PROVIDER=ollama
# OLLAMA_URL=http://localhost:11434

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
python wsgi.py
```

#### 3. Frontend Setup

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

**Keep Ollama running in a separate terminal!**

For detailed Ollama setup and troubleshooting, see [OLLAMA_SETUP.md](OLLAMA_SETUP.md)

---

### Choosing Between Groq and Ollama

| Aspect | Groq | Ollama |
|--------|------|--------|
| **Setup Time** | 2 minutes | 10-15 minutes |
| **Speed** | Very fast | Slow (CPU-based) |
| **Cost** | Free tier | Free (after download) |
| **Internet** | Required | Not required |
| **API Key** | Required (free) | Not required |
| **Best For** | Quick testing & production | Privacy & local development |

**Recommendation**: Start with Groq for fastest setup!

Frontend will be available at: `http://localhost:3000`

## 📖 Usage Guide

### Basic Workflow

1. **Input Resume**:
   - Copy-paste your resume text, or
   - Upload PDF resume file

2. **Input Job Description**:
   - Copy-paste the job description from job posting

3. **Click "Analyze Resume"**:
   - Get comprehensive analysis with match score
   - See matching and missing skills
   - Get actionable improvement suggestions

4. **Optional: Improve Resume**:
   - Click "✨ Improve Resume" to generate optimized version
   - Review and copy the improved resume
   - Download as text file

5. **Optional: Explore Career Paths**:
   - Click "💼 Career Fields" to see career opportunities
   - Discover relevant industries and job titles

6. **Optional: Interview Prep**:
   - Click "🎤 Interview Prep" for interview preparation
   - Review probable questions and sample answers

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# From project root directory

# Create .env file with your API key
echo ANTHROPIC_API_KEY=your_key_here > .env

# Build and start containers
docker-compose up --build

# The application will be available at:
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

### Stop Services

```bash
docker-compose down
```

## 🔌 API Endpoints Reference

### Analysis
```
POST /api/analyze
Content-Type: application/json

{
  "resume": "resume text...",
  "job_description": "job description text..."
}

Response:
{
  "success": true,
  "analysis": {
    "match_percentage": 75,
    "matching_skills": ["Python", "React", ...],
    "missing_skills": ["Docker", ...],
    "improvements": ["Add more metrics...", ...],
    ...
  }
}
```

### Improve Resume
```
POST /api/improve-resume
Content-Type: application/json

{
  "resume": "original resume...",
  "job_description": "target job description...",
  "improvements": ["improvement 1", "improvement 2", ...]
}

Response:
{
  "success": true,
  "improved_resume": "optimized resume text..."
}
```

### Career Fields
```
POST /api/career-fields
Content-Type: application/json

{
  "resume": "resume text..."
}

Response:
{
  "success": true,
  "career_data": {
    "career_fields": ["Data Science", ...],
    "job_titles": ["Data Scientist", ...],
    "industries": ["Tech", ...],
    ...
  }
}
```

### Interview Preparation
```
POST /api/interview-prep
Content-Type: application/json

{
  "resume": "resume text...",
  "job_description": "job description text..."
}

Response:
{
  "success": true,
  "interview_data": {
    "probable_questions": ["Tell us about yourself", ...],
    "expected_answers": {...},
    "focus_areas": ["Python", ...],
    ...
  }
}
```

### PDF Upload
```
POST /api/upload-pdf
Content-Type: multipart/form-data

file: <PDF file>

Response:
{
  "success": true,
  "text": "extracted resume text...",
  "filename": "resume.pdf"
}
```

## 🎨 Frontend Features

### Components
- **ResumeInput**: Text input and PDF upload
- **JobDescriptionInput**: Job description text area
- **AnalysisResults**: Comprehensive analysis display with metrics
- **ImprovedResumeDisplay**: Shows optimized resume with copy/download
- **CareerFieldsDisplay**: Career suggestions with industry info
- **InterviewPrepDisplay**: Interview questions and preparation guide
- **LoadingSpinner**: User feedback during processing
- **ErrorMessage**: Error handling and display

### State Management
- **Zustand Store**: Global state for analysis data
- Persistent across tab switches
- Easy reset functionality

## 📊 Backend Features

### Services
- **ResumeAnalyzerService**: Core AI analysis logic
  - Resume-job matching
  - Resume improvement
  - Career field suggestions
  - Interview preparation

### Utilities
- **PDFParser**: PDF text extraction with validation
- **InputValidator**: Resume and job description validation
- **ResponseParser**: Claude response parsing and JSON extraction

### API Routes
- `/api/health`: Health check
- `/api/analyze`: Main resume analysis
- `/api/improve-resume`: Resume optimization
- `/api/career-fields`: Career suggestions
- `/api/interview-prep`: Interview preparation
- `/api/upload-pdf`: PDF file handling

## 🛡️ Hallucination Prevention

The system includes several mechanisms to minimize AI hallucinations:

1. **Explicit Evidence Requirement**: All analysis claims must be traceable to resume content
2. **Fact-Based Analysis**: Only information explicitly mentioned is analyzed
3. **Input Validation**: Resume and job description lengths are validated
4. **JSON Validation**: Structured responses ensure consistency
5. **Clear Guidance**: AI instructions explicitly forbid speculation
6. **Response Parsing**: Responses are validated before display

## 🐛 Troubleshooting

### API Key Error
```
Error: ANTHROPIC_API_KEY not found
```
**Solution**: Add your API key to `.env` file in backend directory

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port in config or kill process using that port

### CORS Error in Frontend
```
Error: CORS policy
```
**Solution**: Ensure backend is running on port 5000

### PDF Upload Fails
**Solution**: 
- Check file is valid PDF
- Ensure file size < 16MB
- Verify PDFPlumber is installed: `pip install pdfplumber`

### Slow Response Times
**Solution**:
- Check your internet connection
- API response can take 10-30 seconds for complex analysis
- Consider reducing resume/job description length

## 📁 Project Structure

```
AIResumeAnalyzer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── analysis.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   └── resume_analyzer.py
│   │   └── utils/
│   │       ├── pdf_parser.py
│   │       ├── validators.py
│   │       └── parsers.py
│   ├── wsgi.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── HomePage.jsx
│   │   ├── components/
│   │   │   ├── ResumeInput.jsx
│   │   │   ├── JobDescriptionInput.jsx
│   │   │   ├── AnalysisResults.jsx
│   │   │   ├── ImprovedResumeDisplay.jsx
│   │   │   ├── CareerFieldsDisplay.jsx
│   │   │   ├── InterviewPrepDisplay.jsx
│   │   │   └── Common.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── store/
│   │   │   └── analysisStore.js
│   │   ├── styles/
│   │   │   └── index.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── .env.example
│   └── Dockerfile
│
├── docker-compose.yml
├── config.py
└── ARCHITECTURE.md
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `FLASK_ENV=production` in backend `.env`
- [ ] Set `VITE_API_URL` to production backend URL
- [ ] Enable HTTPS for API endpoints
- [ ] Set strong API rate limiting
- [ ] Configure proper error logging
- [ ] Setup environment-based secrets
- [ ] Enable CORS for specific domains only

### Cloud Deployment (Example: Heroku)

**Backend**:
```bash
# Add Procfile
echo "web: gunicorn --bind 0.0.0.0:\$PORT wsgi:app" > Procfile

# Deploy
git push heroku main
```

**Frontend**:
```bash
# Build for production
npm run build

# Deploy to Vercel/Netlify
# Or use static hosting (AWS S3, Cloudflare Pages, etc.)
```

## 📝 Configuration

### Backend Configuration (`backend/.env`)
```
ANTHROPIC_API_KEY=your_api_key_here
FLASK_APP=wsgi.py
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### Frontend Configuration (`frontend/.env`)
```
VITE_API_URL=http://localhost:5000/api
```

## 📚 Additional Resources

- [Anthropic Claude API Docs](https://docs.anthropic.com)
- [React Documentation](https://react.dev)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Tailwind CSS](https://tailwindcss.com)
- [Vite Documentation](https://vitejs.dev)

## 📄 License

This project is provided as-is for educational and commercial use.

## 💬 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation
3. Check console for error messages
4. Verify API key is correctly set

## 🎯 Future Enhancements

- [ ] User authentication and saved analyses
- [ ] Resume templates library
- [ ] Job tracking and application history
- [ ] LinkedIn resume import
- [ ] Cover letter generation
- [ ] Real-time salary insights
- [ ] Company research integration
- [ ] Networking suggestions
- [ ] Skill marketplace recommendations
- [ ] Interview video recording and feedback

---

**Last Updated**: January 2025  
**Version**: 1.0.0
