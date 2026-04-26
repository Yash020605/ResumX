"""
Resume analysis routes.
"""
from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from werkzeug.exceptions import BadRequest
import io

from app.services.job_search import JobSearchService
from app.utils.validators import InputValidator
from app.utils.pdf_parser import PDFParser

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api')

# Rate limiting for analysis endpoints
limiter = Limiter(key_func=lambda: request.remote_addr)

# Lazy import - only import when needed
_resume_analyzer_service = None
import threading

_lock = threading.Lock()

def get_resume_analyzer_service():
    """Get or create GroqAIService instance lazily with thread safety."""
    global _resume_analyzer_service
    if _resume_analyzer_service is None:
        with _lock:
            if _resume_analyzer_service is None:  # Double-check locking
                from app.services.groq_ai_service import GroqAIService
                _resume_analyzer_service = GroqAIService()
    return _resume_analyzer_service


@analysis_bp.route('/analyze', methods=['POST'])
def analyze_resume():
    """
    Analyze resume against job description.
    
    Expected JSON:
    {
        "resume": "resume text",
        "job_description": "job description text"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        resume = data.get('resume', '').strip()
        job_description = data.get('job_description', '').strip()
        
        # Validate inputs
        is_valid, error_msg = InputValidator.validate_both(resume, job_description)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Perform analysis
        service = get_resume_analyzer_service()
        analysis = service.analyze_resume_match(resume, job_description)
        
        if "error" in analysis:
            return jsonify(analysis), 500
        
        return jsonify({
            "success": True,
            "analysis": analysis
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@analysis_bp.route('/improve-resume', methods=['POST'])
def improve_resume():
    """
    Generate improved version of resume.
    
    Expected JSON:
    {
        "resume": "original resume text",
        "job_description": "target job description",
        "improvements": ["improvement 1", "improvement 2", ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        resume = data.get('resume', '').strip()
        job_description = data.get('job_description', '').strip()
        improvements = data.get('improvements', [])
        
        print(f"Improve resume request received:")
        print(f"  Resume length: {len(resume)}")
        print(f"  Job description length: {len(job_description)}")
        print(f"  Improvements count: {len(improvements)}")
        
        # Validate resume and job description
        is_valid, error_msg = InputValidator.validate_both(resume, job_description)
        if not is_valid:
            print(f"  Validation failed: {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        if improvements is None:
            improvements = ["Optimize resume formatting and wording to better match the job description"]
        elif isinstance(improvements, str):
            improvements = [improvements]
        elif not isinstance(improvements, list):
            return jsonify({"error": "Improvements must be a list of suggestions"}), 400
            
        if not improvements:
            improvements = ["Optimize resume formatting and wording to better match the job description"]
        
        print(f"  Validation passed, generating improved resume...")
        
        # Generate improved resume
        service = get_resume_analyzer_service()
        result = service.generate_improved_resume(resume, job_description, improvements)
        
        print(f"  Result: success={result.get('success')}")
        
        return jsonify(result), 200 if result.get("success") else 500
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Resume improvement error: {error_details}")
        return jsonify({"error": f"Resume improvement failed: {str(e)}"}), 500


@analysis_bp.route('/career-fields', methods=['POST'])
def get_career_fields():
    """
    Get career field suggestions based on resume.
    
    Expected JSON:
    {
        "resume": "resume text"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        resume = data.get('resume', '').strip()
        
        # Validate resume
        is_valid, error_msg = InputValidator.validate_resume(resume)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Get career suggestions
        service = get_resume_analyzer_service()
        career_data = service.get_career_fields(resume)
        
        if "error" in career_data:
            return jsonify(career_data), 500
        
        return jsonify({
            "success": True,
            "career_data": career_data
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Career analysis failed: {str(e)}"}), 500


@analysis_bp.route('/interview-prep', methods=['POST'])
def get_interview_prep():
    """
    Generate interview preparation guide.
    
    Expected JSON:
    {
        "resume": "resume text",
        "job_description": "job description text"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        resume = data.get('resume', '').strip()
        job_description = data.get('job_description', '').strip()
        
        # Validate inputs
        is_valid, error_msg = InputValidator.validate_both(resume, job_description)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Generate interview prep
        service = get_resume_analyzer_service()
        interview_data = service.generate_interview_prep(resume, job_description)
        
        if "error" in interview_data:
            return jsonify(interview_data), 500
        
        return jsonify({
            "success": True,
            "interview_data": interview_data
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Interview prep generation failed: {str(e)}"}), 500


@analysis_bp.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """
    Handle PDF file upload and extract text.
    
    Expected: multipart/form-data with 'file' field
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "File must be a PDF"}), 400
        
        # Validate PDF
        file.seek(0)
        if not PDFParser.validate_pdf(file):
            return jsonify({"error": "Invalid or empty PDF file"}), 400
        
        # Extract text
        file.seek(0)
        text = PDFParser.extract_text(file)
        
        if not text:
            return jsonify({"error": "Could not extract text from PDF"}), 400
        
        return jsonify({
            "success": True,
            "text": text,
            "filename": file.filename
        }), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"PDF upload failed: {str(e)}"}), 500

@analysis_bp.route('/search-jobs', methods=['POST'])
def search_jobs():
    """
    Search for jobs matching the resume.
    
    Expected JSON:
    {
        "resume": "resume text"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        resume = data.get('resume', '').strip()
        job_description = data.get('job_description', '').strip()
        
        # Validate input
        if not resume or len(resume) < 50:
            return jsonify({"error": "Resume text is required and should be at least 50 characters"}), 400
        
        # Perform job search
        service = JobSearchService()
        result = service.get_matching_jobs(resume, job_description)
        
        return jsonify(result), 200 if result.get("success") else 500
    
    except Exception as e:
        return jsonify({"error": f"Job search failed: {str(e)}"}), 500


@analysis_bp.route('/suggest-projects', methods=['POST'])
def suggest_projects():
    """
    Suggest relevant projects based on resume and job analysis.
    
    Expected JSON:
    {
        "resume": "resume text",
        "job_description": "job description text (optional)",
        "matching_skills": ["skill1", "skill2"] (optional),
        "missing_skills": ["skill1", "skill2"] (optional),
        "career_fields": ["field1", "field2"] (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        resume = data.get('resume', '').strip()
        job_description = data.get('job_description', '').strip()
        matching_skills = data.get('matching_skills', [])
        missing_skills = data.get('missing_skills', [])
        career_fields = data.get('career_fields', [])
        
        print(f"Project suggestion request received:")
        print(f"  Resume length: {len(resume)}")
        print(f"  Job description length: {len(job_description)}")
        print(f"  Matching skills: {len(matching_skills)}")
        print(f"  Missing skills: {len(missing_skills)}")
        print(f"  Career fields: {len(career_fields)}")
        
        # Validate resume
        if not resume or len(resume) < 50:
            return jsonify({"error": "Resume text is required and should be at least 50 characters"}), 400
        
        # Import and use project suggestion service
        from app.services.project_suggestion_service import ProjectSuggestionService
        
        try:
            print("Initializing ProjectSuggestionService...")
            service = ProjectSuggestionService()
            print(f"Service initialized. AI available: {service.ai_model is not None}")
        except Exception as init_error:
            print(f"Failed to initialize ProjectSuggestionService: {init_error}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Service initialization failed: {str(init_error)}"}), 500
        
        print("Calling suggest_projects...")
        result = service.suggest_projects(
            resume=resume,
            job_description=job_description,
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            career_fields=career_fields
        )
        
        print(f"Result: success={result.get('success')}, projects={result.get('total', 0)}")
        
        return jsonify(result), 200 if result.get("success") else 500
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Project suggestion error: {error_details}")
        return jsonify({"error": f"Project suggestion failed: {str(e)}"}), 500


@analysis_bp.route('/test-projects', methods=['GET'])
def test_projects():
    """Test endpoint to verify project suggestion service is working."""
    try:
        from app.services.project_suggestion_service import ProjectSuggestionService
        service = ProjectSuggestionService()
        
        total_projects = sum(len(cat["projects"]) for cat in service.project_knowledge_base)
        
        return jsonify({
            "success": True,
            "message": "Project suggestion service is working",
            "ai_available": service.ai_model is not None,
            "categories": len(service.project_knowledge_base),
            "total_projects": total_projects
        }), 200
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@analysis_bp.route('/evaluate-answer', methods=['POST'])
def evaluate_answer():
    """
    Evaluate a candidate's answer to an interview question.
    
    Expected JSON:
    {
        "resume": "resume text",
        "question": "interview question text",
        "answer": "candidate answer text"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        resume = data.get('resume', '').strip()
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        
        if not resume or not question or not answer:
            return jsonify({"error": "Resume, question, and answer are required"}), 400
            
        service = get_resume_analyzer_service()
        evaluation = service.evaluate_interview_answer(question, answer, resume)
        
        if "error" in evaluation:
            return jsonify(evaluation), 500
            
        return jsonify({
            "success": True,
            "evaluation": evaluation
        }), 200
    except Exception as e:
        return jsonify({"error": f"Answer evaluation failed: {str(e)}"}), 500


@analysis_bp.route('/chat', methods=['POST'])
def chat():
    """Career coach chatbot — uses the LLM provider (Groq → Gemini fallback)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        history = data.get('messages', [])
        if not history:
            return jsonify({"error": "messages array is required"}), 400

        from app.agents.llm_provider import get_llm
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        system = SystemMessage(content=(
            "You are ResumX Career Coach — a sharp, friendly AI career advisor. "
            "Give concise, actionable advice. Use plain text only — NO markdown, "
            "NO asterisks, NO bullet symbols. Use short paragraphs. "
            "Topics: resume writing, interview prep, career paths, salary negotiation, skill gaps."
        ))

        lc_messages = [system]
        for m in history[-12:]:
            role    = m.get("role", "user")
            content = m.get("content", "")
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role in ("assistant", "bot"):
                lc_messages.append(AIMessage(content=content))

        llm   = get_llm(temperature=0.7, max_tokens=400)
        reply = llm.invoke(lc_messages).content.strip()

        # Strip any residual markdown asterisks
        import re
        reply = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', reply)
        reply = re.sub(r'^#{1,3}\s+', '', reply, flags=re.MULTILINE)

        return jsonify({"reply": reply}), 200

    except Exception as e:
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500
