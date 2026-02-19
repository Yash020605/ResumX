# AI Resume Analyzer

A sophisticated, production-ready AI-powered resume analysis and optimization platform with React frontend and Python backend that helps job seekers maximize their chances of getting hired.

## 🎯 What It Does

### 📊 **Comprehensive Resume Analysis**
- Analyzes your resume against job descriptions with detailed feedback
- Provides match scoring (0-100%) with visual representation
- Identifies key strengths and critical gaps
- Detailed skill gap analysis with importance levels
- Specific, actionable improvement suggestions

### ✨ **AI-Powered Resume Optimization**
- Generates improved resume versions tailored to job requirements
- Maintains authenticity (no false claims added)
- ATS-friendly formatting for better applicant tracking
- Natural keyword integration from job description
- Professional rephrasing and restructuring

### 💼 **Career Path Discovery**
- Suggests 5-7 relevant career fields with explanations
- Recommends 10-15 job titles to search for
- Identifies high-value industries for your skills
- Growth opportunity identification
- Skill development recommendations
- Relevant certifications to pursue

### 🎤 **Interview Preparation**
- Generates 8-12 probable interview questions
- Provides sample answers based on your resume
- Identifies key focus areas for preparation
- Common interview mistakes to avoid
- Key strengths to emphasize
- Study resource recommendations

## 🏗️ Architecture

**Full-Stack Application:**
- **Frontend**: React 18 with Vite, Tailwind CSS, Zustand state management
- **Backend**: Python Flask REST API with Groq or Ollama AI
- **AI Providers**: 
  - **Groq** (Cloud): Free tier, instant setup, very fast (recommended)
  - **Ollama** (Local): Completely free, runs locally, privacy-focused
- **Deployment**: Docker & Docker Compose support
- **Database**: N/A (Stateless API design)

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 18.x or higher
- **One of:**
  - Groq API key (free at https://console.groq.com - takes 1 minute)
  - OR Ollama installed locally (https://ollama.ai)

### 1-Minute Setup with Groq

#### Windows
```bash
# Get your free Groq API key from https://console.groq.com
# Then run:
$env:GROQ_API_KEY = "your_groq_key"

# Run the quick start script
.\start.bat
```

#### Mac/Linux
```bash
# Get your free Groq API key from https://console.groq.com
export GROQ_API_KEY="your_groq_key"

chmod +x start.sh
./start.sh
```

Then open: **http://localhost:5173**

### Manual Setup with Groq

**Backend Setup:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo AI_PROVIDER=groq > .env
echo GROQ_API_KEY=your_groq_key_here >> .env

# Run backend
python wsgi.py
```

### Local Setup with Ollama

First, download Ollama from https://ollama.ai then:

```bash
# In terminal 1: Start Ollama
ollama pull mistral
ollama serve

# In terminal 2: Backend setup
cd backend
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Create .env file
echo AI_PROVIDER=ollama > .env
echo OLLAMA_URL=http://localhost:11434 >> .env

python wsgi.py
```

**Frontend Setup (new terminal):**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Then open: **http://localhost:3000**

### Docker Setup

```bash
# Set your API key
echo ANTHROPIC_API_KEY=your_key_here > .env

# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:3000
```

## 📖 Usage Guide

### Basic Workflow

1. **Enter Your Resume**
   - Paste resume text directly, or
   - Upload PDF resume file
   - System extracts and validates content

2. **Enter Job Description**
   - Copy and paste from job posting
   - Include full description for best analysis

3. **Click "Analyze Resume"**
   - Get match score (0-100%)
   - See matching and missing skills
   - Get improvement suggestions
   - View career field recommendations

4. **Optional: Improve Resume**
   - Click "✨ Improve Resume"
   - Review optimized version
   - Copy or download improved resume

5. **Optional: Career & Interview Prep**
   - Click "💼 Career Fields" for career suggestions
   - Click "🎤 Interview Prep" for interview preparation
   - Get probable questions and sample answers

## 🔌 API Endpoints

### Analysis Endpoint
```
POST /api/analyze
Content-Type: application/json

{
  "resume": "resume text...",
  "job_description": "job description..."
}
```

### All Available Endpoints
- `POST /api/analyze` - Analyze resume vs job description
- `POST /api/improve-resume` - Generate optimized resume
- `POST /api/career-fields` - Get career suggestions
- `POST /api/interview-prep` - Get interview preparation
- `POST /api/upload-pdf` - Upload and extract PDF
- `GET /api/health` - Health check

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed API documentation.

## 📊 Technology Stack

**Frontend:**
- React 18.2
- Vite 5.0
- Tailwind CSS 3
- Zustand (State Management)
- Axios (HTTP Client)
- Lucide React (Icons)

#### 📊 Analysis Results Tab
- **Match Percentage**: 0-100% match score
- **Matching Skills**: Skills from your resume that match job requirements
- **Missing Skills**: Important skills you should develop
- **Key Strengths**: Your top qualifications highlighted

#### 💼 Career Fields Tab
- 5-7 recommended career fields for your skill set
- Specific job titles to search for
- Industries where your skills are highly valued
- Growth opportunities and suggestions

#### ✨ Improved Resume Tab
- AI-generated optimized resume tailored to the job
- Click "🚀 Generate Improved Resume" to create it
- Download the improved resume as a text file

#### 🎯 Interview Preparation Tab
- **Alumni Insights**: Questions based on real interview experiences
- 8-10 probable interview questions with sample answers
- Key topics to prepare for
- Common follow-up questions
- Red flags to avoid
- Click "🚀 Generate Interview Guide" to create it
- Download the complete interview preparation guide

#### 📈 Detailed Feedback Tab
- Comprehensive feedback on resume-job alignment
- Specific, actionable improvements
- Tips for optimizing your resume further

## Example Workflow

1. **Upload your resume** (PDF or text) or paste your current resume
2. **Find a job posting** that interests you
3. **Analyze the match** - get your score and feedback
4. **Review career fields** you qualify for
5. **Generate improved resume** tailored to the job
6. **Prepare for interviews** with probable questions and sample answers
7. **Download** both the optimized resume and interview guide

## Key Features Explained

### Match Percentage
- **80-100%**: Excellent fit - you're well-qualified
- **60-79%**: Good fit - consider addressing missing skills
- **Below 60%**: Consider additional training or targeting different roles

### Skill Analysis
- **Matching Skills**: Already present in your resume
- **Missing Skills**: Important for the role but not in your resume

### AI Resume Generation
- Uses Claude AI to optimize your resume
- Maintains truthfulness - no fake credentials added
- Improves formatting and keyword inclusion
- Makes your resume ATS-friendly (Applicant Tracking System)

## Hallucination Prevention

The application is designed to minimize AI hallucinations:
- Specific prompts that demand factual analysis
- Clear constraints preventing false information
- All analysis based on actual resume and job description content
- No speculative or assumed qualifications added

## Tips for Best Results

1. **Detailed Resumes**: More detail in your resume leads to better analysis
2. **Complete Job Descriptions**: Full job descriptions give more comprehensive analysis
3. **Key Skills**: Make sure important skills are clearly mentioned in your resume
4. **Experience Details**: Include specific achievements and technologies used
5. **Formatting**: Use clear section headers for better AI understanding

## Troubleshooting

### "ANTHROPIC_API_KEY not found" Error
- Make sure you've set the environment variable correctly
- Restart your terminal/PowerShell after setting the variable
- Check that your API key is correct

### Application Won't Start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)
- Try clearing Streamlit cache: `streamlit cache clear`

### Analysis Takes Too Long
- Large resumes and job descriptions may take longer
- Try breaking them into smaller sections
- Check your internet connection

### Poor Analysis Quality
- Ensure your resume has clear structure and details
- Include specific skills and technologies
- Use the full job description (not just summary)

## File Structure

```
AIResumeAnalyzer/
├── ResumeAI.py          # Main application file
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## API Costs

This application uses the Claude API, which is a paid service:
- Pricing is based on tokens used
- Each analysis typically costs less than $0.02
- Monitor your usage at https://console.anthropic.com

## Future Enhancements

Potential features for v2.0:
- PDF generation for improved resume and interview guide
- Resume history and comparison
- Batch job matching (compare multiple jobs)
- Skill development roadmap with learning resources
- Video interview practice with AI feedback
- LinkedIn profile optimization suggestions
- Portfolio suggestions based on job requirements

## Support & Feedback

If you encounter issues or have suggestions:
1. Check the Troubleshooting section
2. Verify your Anthropic API key is active
3. Ensure all dependencies are correctly installed

## License

This project is part of the TechGeek learning initiative.

---

**Happy optimizing! 🚀 May your resume match every opportunity you deserve!**
