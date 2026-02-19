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
        
        # Validate resume and job description
        is_valid, error_msg = InputValidator.validate_both(resume, job_description)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        if not improvements or not isinstance(improvements, list):
            return jsonify({"error": "Improvements must be a non-empty list"}), 400
        
        # Generate improved resume
        service = get_resume_analyzer_service()
        result = service.generate_improved_resume(resume, job_description, improvements)
        
        return jsonify(result), 200 if result.get("success") else 500
    
    except Exception as e:
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
        
        # Validate input
        if not resume or len(resume) < 50:
            return jsonify({"error": "Resume text is required and should be at least 50 characters"}), 400
        
        # Perform job search
        service = JobSearchService()
        result = service.get_matching_jobs(resume)
        
        return jsonify(result), 200 if result.get("success") else 500
    
    except Exception as e:
        return jsonify({"error": f"Job search failed: {str(e)}"}), 500