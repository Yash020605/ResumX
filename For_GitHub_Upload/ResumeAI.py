"""Create a resume analysis using AI.
The application takes the resume from the user and analyzes it according to the job requirement on upwork platform or any other freelancing platform. 
It provides feedback on how well the resume matches the job description and suggests improvements.
It also highlights key skills and experiences that should be emphasized to increase the chances of getting hired.
Also provides the fields in which the user can apply on the basis of the resume
Also make the changes in the resume at the end according to the job description provided by the user.(if user wants)
Use streamlit for the web app interface.
Use python structured programming for the backend logic.
for AI use claude 
also keep the halucinations minimum while providing the analysis.
"""

import streamlit as st
import os
from groq import Groq
import pdfplumber

# ===================== CONFIGURATION =====================
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for attractive UI
st.markdown("""
    <style>
    /* Overall Theme */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #ec4899;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
    }
    
    /* Main Background */
    .main {
        background: linear-gradient(135deg, #f0f9ff 0%, #faf5ff 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    /* Sidebar Text */
    [data-testid="stSidebar"] .stMarkdownContainer {
        color: #f8fafc;
    }
    
    [data-testid="stSidebar"] h2 {
        color: #e0e7ff !important;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #6366f1;
        padding-bottom: 0.5rem;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #c7d2fe !important;
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 1.5rem;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(90deg, rgba(99,102,241,0.05) 0%, rgba(139,92,246,0.05) 100%);
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        height: 50px;
        padding: 8px 20px !important;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        color: #64748b;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: rgba(99,102,241,0.1);
        border-color: #6366f1;
        color: #6366f1;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
        border-color: #6366f1;
    }
    
    /* Button Styling */
    .stButton > button {
        width: 100%;
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(99,102,241,0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        background-color: #f8fafc;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1;
        background-color: white;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
    }
    
    /* Radio Button */
    .stRadio > label {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #e0e7ff;
    }
    
    .stRadio > label:hover {
        background-color: rgba(99,102,241,0.15);
    }
    
    /* Metric Cards */
    .stMetric {
        background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(139,92,246,0.05) 100%);
        border-radius: 12px;
        padding: 20px;
        border: 2px solid rgba(99,102,241,0.2);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        border-color: #6366f1;
        box-shadow: 0 8px 16px rgba(99,102,241,0.15);
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #6366f1;
        font-weight: 700;
    }
    
    /* Success/Warning/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(16,185,129,0.05) 100%);
        border: 2px solid #10b981;
        border-radius: 10px;
        padding: 12px;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245,158,11,0.1) 0%, rgba(245,158,11,0.05) 100%);
        border: 2px solid #f59e0b;
        border-radius: 10px;
        padding: 12px;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239,68,68,0.1) 0%, rgba(239,68,68,0.05) 100%);
        border: 2px solid #ef4444;
        border-radius: 10px;
        padding: 12px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(99,102,241,0.05) 100%);
        border: 2px solid #6366f1;
        border-radius: 10px;
        padding: 12px;
    }
    
    /* Divider */
    .stDivider {
        background: linear-gradient(90deg, transparent 0%, #6366f1 50%, transparent 100%);
        height: 2px;
        margin: 24px 0;
    }
    
    /* Download Button */
    [data-testid="stDownloadButton"] > button {
        width: 100%;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(16,185,129,0.3);
    }
    
    /* File Uploader */
    [data-testid="stFileUploadDropzone"] {
        border-radius: 12px;
        border: 2px dashed #6366f1;
        background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(139,92,246,0.05) 100%);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #8b5cf6;
        background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.1) 100%);
    }
    
    /* Markdown Content */
    .stMarkdownContainer {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #334155;
    }
    
    h1 {
        color: #1e293b;
        font-weight: 800;
        font-size: 2.5rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
    }
    
    h2 {
        color: #1e293b;
        font-weight: 700;
        font-size: 1.5rem;
        margin-top: 24px;
        margin-bottom: 12px;
        border-bottom: 3px solid #6366f1;
        padding-bottom: 8px;
    }
    
    h3 {
        color: #334155;
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 16px;
    }
    
    /* Expander */
    .stExpander {
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        background-color: #f8fafc;
    }
    
    .stExpander > div > div > button {
        font-weight: 600;
        color: #6366f1;
    }
    
    /* Text Area */
    .stTextArea [data-baseweb="textarea"] {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        background-color: #f8fafc;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f0f9ff;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #4f46e5 0%, #7c3aed 100%);
    }
    
    /* Animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main > div > div > div > div {
        animation: fadeIn 0.5s ease-in-out;
    }
    </style>
""", unsafe_allow_html=True)

# ===================== HELPER FUNCTIONS =====================

def initialize_client():
    """Initialize Groq client with API key."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ GROQ_API_KEY not found. Please set it in your environment variables.")
        st.stop()
    return Groq(api_key=api_key)

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF file."""
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"❌ Error extracting PDF: {str(e)}")
        return None

def analyze_resume_match(client, resume: str, job_description: str) -> dict:
    """Analyze how well resume matches job description."""
    conversation_history = []
    
    # First message: Get initial analysis
    analysis_prompt = f"""Analyze the following resume against the job description provided. 
Be precise and fact-based. Avoid hallucinations and speculation.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

Provide a JSON-formatted response with exactly these fields:
1. match_percentage (0-100)
2. matching_skills (list of skills from resume that match job requirements)
3. missing_skills (list of important skills from job description that resume lacks)
4. feedback (detailed feedback on resume match)
5. improvements (specific actionable improvements for the resume)
6. career_fields (list of 5-7 career fields this resume qualifies for)
7. key_strengths (3-5 key strengths highlighted in the resume)

Format: Start with ```json and end with ```"""
    
    conversation_history.append({
        "role": "user",
        "content": analysis_prompt
    })
    
    response = client.messages.create(
        model="mixtral-8x7b-32768",
        max_tokens=2000,
        system="""You are an expert resume analyst and career counselor with deep knowledge of the job market.
Your role is to provide accurate, actionable feedback on resumes. Always be specific and fact-based.
Never make assumptions about qualifications not explicitly mentioned in the resume.
Format all analysis responses as valid JSON for easy parsing.""",
        messages=conversation_history
    )
    
    assistant_response = response.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": assistant_response
    })
    
    return {
        "analysis": assistant_response,
        "history": conversation_history
    }

def generate_improved_resume(client, resume: str, job_description: str, improvements: str, conversation_history: list) -> str:
    """Generate an improved version of the resume."""
    improvement_prompt = f"""Based on the previous analysis and the following improvements needed, 
please rewrite the resume to better match the job description while maintaining authenticity and accuracy.

Original Resume:
{resume}

Improvements to make:
{improvements}

Job Description:
{job_description}

Rules:
- Keep all true information from the original resume
- Reformat and reword to better highlight relevant skills
- Add missing but relevant keywords from job description
- Use professional language and ATS-friendly formatting
- Do NOT add false qualifications or experience
- Start with "```" to mark the beginning and end with "```" to mark the end

Improved Resume:"""
    
    conversation_history.append({
        "role": "user",
        "content": improvement_prompt
    })
    
    response = client.messages.create(
        model="mixtral-8x7b-32768",
        max_tokens=2500,
        system="""You are an expert resume writer who specializes in optimizing resumes for job matching.
Your goal is to help candidates present their qualifications effectively.
Always maintain truthfulness - never add false experience or qualifications.
Format resumes professionally and ensure they're ATS-friendly.""",
        messages=conversation_history
    )
    
    improved_resume = response.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": improved_resume
    })
    
    return improved_resume

def get_career_guidance(client, resume: str, conversation_history: list) -> str:
    """Get career field suggestions based on resume."""
    guidance_prompt = f"""Based on this resume, suggest specific career fields and roles the candidate should consider.

Resume:
{resume}

Please provide:
1. Top 5-7 career fields (with brief explanation why)
2. Specific job titles to search for
3. Industries where these skills are highly valued
4. Growth opportunities based on current skills
5. Certifications or skills that would enhance career prospects"""
    
    conversation_history.append({
        "role": "user",
        "content": guidance_prompt
    })
    
    response = client.messages.create(
        model="mixtral-8x7b-32768",
        max_tokens=1500,
        system="""You are a career counselor with expertise in matching skills to job markets.
Provide practical, actionable career guidance based on resume content.
Be specific about industries and job titles.""",
        messages=conversation_history
    )
    
    career_guidance = response.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": career_guidance
    })
    
    return career_guidance

def generate_interview_questions(client, resume: str, job_description: str, conversation_history: list) -> str:
    """Generate probable interview questions based on resume and job description.
    
    This simulates insights gathered from alumni who have interviewed for similar roles.
    Provides realistic questions and concise model answers."""
    
    interview_prompt = f"""You are an experienced alumni recruiter who has conducted interviews for this role multiple times.
Based on your experience, provide the most probable interview questions and concise model answers.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

Please structure your response as:

**📋 PROBABLE INTERVIEW QUESTIONS & SAMPLE ANSWERS**

Provide 8-10 questions that would likely be asked in an interview for this role. For each question:
1. The question itself
2. Why it's likely to be asked (based on role requirements)
3. A concise model answer (2-3 sentences) based on the resume and job requirements

Format each as:
**Q[number]: [Question]**
*Why asked:* [Explanation]
*Sample Answer:* [Concise answer]
---

Also include:
- **Key Topics to Prepare**: Main technical/soft skill areas to study
- **Common Follow-up Questions**: 3-5 follow-up questions for the main questions
- **Red Flags to Avoid**: Common mistakes candidates make for this role"""
    
    conversation_history.append({
        "role": "user",
        "content": interview_prompt
    })
    
    response = client.messages.create(
        model="mixtral-8x7b-32768",
        max_tokens=3000,
        system="""You are a veteran recruiter and alumni mentor helping candidates prepare for interviews.
Your questions are based on real interview experiences from similar positions.
Provide practical, honest preparation guidance.
Keep answers concise but comprehensive (2-3 sentences for each answer).
Focus on both technical and behavioral aspects.""",
        messages=conversation_history
    )
    
    interview_guide = response.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": interview_guide
    })
    
    return interview_guide

# ===================== MAIN APPLICATION =====================

def main():
    st.title("📄 AI Resume Analyzer")
    st.markdown("---")
    
    # Add decorative header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.1) 100%); border-radius: 15px; border: 2px solid rgba(99,102,241,0.2);">
            <p style="font-size: 1.1rem; color: #334155; margin: 0; font-weight: 500;">
            🚀 AI-Powered Resume Optimization & Interview Preparation
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize Anthropic client
    client = initialize_client()
    
    # Initialize session state
    if "analysis_done" not in st.session_state:
        st.session_state.analysis_done = False
    if "improved_resume" not in st.session_state:
        st.session_state.improved_resume = None
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # Sidebar for input
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <p style="font-size: 2rem; margin: 0;">📋</p>
            <h2 style="margin: 10px 0 0 0; border: none;">Input Data</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Resume")
        resume_input_method = st.radio("Choose input method:", ["📝 Text", "📁 PDF File"], key="resume_method")
        
        resume_input = ""
        if resume_input_method == "📝 Text":
            resume_input = st.text_area(
                "Paste your resume here:",
                height=200,
                placeholder="Enter your resume content...",
                key="resume_input"
            )
        else:
            st.markdown("**Upload your resume PDF:**")
            uploaded_file = st.file_uploader(
                "Select PDF file",
                type="pdf",
                key="pdf_upload"
            )
            if uploaded_file is not None:
                extracted_text = extract_text_from_pdf(uploaded_file)
                if extracted_text:
                    st.success("✅ PDF uploaded successfully!")
                    resume_input = extracted_text
                    # Show preview
                    with st.expander("📄 Preview extracted text"):
                        st.text(resume_input[:500] + "..." if len(resume_input) > 500 else resume_input)
        
        st.markdown("### Job Description")
        job_desc_input = st.text_area(
            "Paste the job description here:",
            height=200,
            placeholder="Enter the job description...",
            key="job_desc_input"
        )
        
        st.markdown("")
        st.markdown("")
        
        # Analyze button with enhanced styling
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔍 Analyze", use_container_width=True, key="analyze_btn"):
                if not resume_input.strip() or not job_desc_input.strip():
                    st.warning("⚠️ Please enter both resume and job description.")
                else:
                    with st.spinner("🤖 Analyzing your resume..."):
                        try:
                            result = analyze_resume_match(client, resume_input, job_desc_input)
                            st.session_state.analysis_result = result["analysis"]
                            st.session_state.conversation_history = result["history"]
                            st.session_state.analysis_done = True
                            st.session_state.resume_text = resume_input
                            st.session_state.job_desc_text = job_desc_input
                            st.success("✅ Analysis complete!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"❌ Error during analysis: {str(e)}")
    
    # Main content area
    if st.session_state.analysis_done:
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Analysis Results",
            "💼 Career Fields",
            "✨ Improved Resume",
            "🎯 Interview Prep",
            "📈 Detailed Feedback"
        ])
        
        with tab1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(139,92,246,0.05) 100%); 
                        padding: 20px; border-radius: 12px; border: 2px solid rgba(99,102,241,0.2);">
                <h2 style="margin: 0 0 10px 0; border: none;">📊 Resume Match Analysis</h2>
                <p style="color: #64748b; margin: 0;">Comprehensive analysis of your resume against the job requirements</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            
            # Extract and display analysis
            analysis_text = st.session_state.analysis_result
            
            # Try to extract JSON from the response
            try:
                import json
                json_start = analysis_text.find("```json")
                json_end = analysis_text.find("```", json_start + 7)
                
                if json_start != -1 and json_end != -1:
                    json_str = analysis_text[json_start + 7:json_end].strip()
                    analysis_data = json.loads(json_str)
                    
                    # Display match percentage with color coding
                    match_pct = analysis_data.get("match_percentage", 0)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        # Color code based on percentage
                        if match_pct >= 80:
                            color = "green"
                        elif match_pct >= 60:
                            color = "orange"
                        else:
                            color = "red"
                        
                        st.metric(
                            "📊 Match Percentage",
                            f"{match_pct}%",
                            delta=None
                        )
                    
                    with col2:
                        st.metric(
                            "✅ Matching Skills",
                            len(analysis_data.get("matching_skills", []))
                        )
                    
                    with col3:
                        st.metric(
                            "❌ Missing Skills",
                            len(analysis_data.get("missing_skills", []))
                        )
                    
                    st.divider()
                    
                    # Matching Skills
                    st.markdown("### ✅ Skills That Match")
                    matching = analysis_data.get("matching_skills", [])
                    if matching:
                        cols = st.columns(2)
                        for idx, skill in enumerate(matching):
                            with cols[idx % 2]:
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(16,185,129,0.05) 100%);
                                            padding: 12px; border-radius: 8px; border-left: 4px solid #10b981;">
                                    <p style="margin: 0; color: #10b981; font-weight: 600;">✓ {skill}</p>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No direct skill matches found.")
                    
                    st.divider()
                    
                    # Missing Skills
                    st.markdown("### ❌ Skills to Develop")
                    missing = analysis_data.get("missing_skills", [])
                    if missing:
                        cols = st.columns(2)
                        for idx, skill in enumerate(missing):
                            with cols[idx % 2]:
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, rgba(245,158,11,0.1) 0%, rgba(245,158,11,0.05) 100%);
                                            padding: 12px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                                    <p style="margin: 0; color: #d97706; font-weight: 600;">⚠ {skill}</p>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.success("You have all the required skills!")
                    
                    st.divider()
                    
                    # Key Strengths
                    st.markdown("### 💪 Key Strengths")
                    strengths = analysis_data.get("key_strengths", [])
                    for i, strength in enumerate(strengths, 1):
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.1) 100%);
                                    padding: 14px; border-radius: 8px; border-left: 4px solid #6366f1; margin-bottom: 10px;">
                            <p style="margin: 0; color: #6366f1; font-weight: 600;">⭐ {strength}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                else:
                    st.write(analysis_text)
            except (json.JSONDecodeError, ValueError):
                st.write(analysis_text)
        
        with tab2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(139,92,246,0.05) 100%); 
                        padding: 20px; border-radius: 12px; border: 2px solid rgba(99,102,241,0.2);">
                <h2 style="margin: 0 0 10px 0; border: none;">💼 Recommended Career Fields</h2>
                <p style="color: #64748b; margin: 0;">Discover career paths that match your skill set and experience</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            
            # Get career guidance if not already done
            if "career_guidance" not in st.session_state:
                with st.spinner("Generating career recommendations..."):
                    try:
                        guidance = get_career_guidance(
                            client,
                            st.session_state.resume_text,
                            st.session_state.conversation_history.copy()
                        )
                        st.session_state.career_guidance = guidance
                    except Exception as e:
                        st.error(f"❌ Error generating guidance: {str(e)}")
                        guidance = None
            
            if "career_guidance" in st.session_state:
                st.write(st.session_state.career_guidance)
        
        with tab3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(139,92,246,0.05) 100%); 
                        padding: 20px; border-radius: 12px; border: 2px solid rgba(99,102,241,0.2);">
                <h2 style="margin: 0 0 10px 0; border: none;">✨ AI-Enhanced Resume</h2>
                <p style="color: #64748b; margin: 0;">Get an optimized version tailored to the job description</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            
            col1, col2 = st.columns([3, 1])
            
            with col2:
                if st.button("🚀 Generate Improved Resume", use_container_width=True):
                    with st.spinner("Creating improved resume..."):
                        try:
                            improved = generate_improved_resume(
                                client,
                                st.session_state.resume_text,
                                st.session_state.job_desc_text,
                                st.session_state.analysis_result,
                                st.session_state.conversation_history.copy()
                            )
                            st.session_state.improved_resume = improved
                        except Exception as e:
                            st.error(f"❌ Error generating resume: {str(e)}")
            
            if st.session_state.improved_resume:
                st.text_area(
                    "Improved Resume:",
                    value=st.session_state.improved_resume,
                    height=500,
                    disabled=True
                )
                
                st.download_button(
                    label="⬇️ Download Improved Resume",
                    data=st.session_state.improved_resume,
                    file_name="improved_resume.txt",
                    mime="text/plain"
                )
            else:
                st.info("👆 Click the button above to generate an AI-enhanced version of your resume.")
        
        with tab4:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(139,92,246,0.05) 100%); 
                        padding: 20px; border-radius: 12px; border: 2px solid rgba(99,102,241,0.2);">
                <h2 style="margin: 0 0 10px 0; border: none;">🎯 Interview Preparation Guide</h2>
                <p style="color: #64748b; margin: 0;">💡 <strong>Alumni Insights:</strong> Questions and answers based on real interview experiences</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            
            col1, col2 = st.columns([3, 1])
            
            with col2:
                if st.button("🚀 Generate Interview Guide", use_container_width=True):
                    with st.spinner("Creating interview preparation guide..."):
                        try:
                            interview_guide = generate_interview_questions(
                                client,
                                st.session_state.resume_text,
                                st.session_state.job_desc_text,
                                st.session_state.conversation_history.copy()
                            )
                            st.session_state.interview_guide = interview_guide
                        except Exception as e:
                            st.error(f"❌ Error generating interview guide: {str(e)}")
            
            if "interview_guide" in st.session_state:
                st.markdown(st.session_state.interview_guide)
                
                st.divider()
                
                st.download_button(
                    label="⬇️ Download Interview Guide",
                    data=st.session_state.interview_guide,
                    file_name="interview_preparation_guide.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.info("👆 Click the button above to generate an AI-powered interview preparation guide based on probable questions from alumni experiences.")
        
        with tab5:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(139,92,246,0.05) 100%); 
                        padding: 20px; border-radius: 12px; border: 2px solid rgba(99,102,241,0.2);">
                <h2 style="margin: 0 0 10px 0; border: none;">📈 Detailed Feedback & Improvements</h2>
                <p style="color: #64748b; margin: 0;">Deep insights and actionable recommendations to optimize your resume</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            
            # Extract and display detailed feedback
            analysis_text = st.session_state.analysis_result
            
            try:
                import json
                json_start = analysis_text.find("```json")
                json_end = analysis_text.find("```", json_start + 7)
                
                if json_start != -1 and json_end != -1:
                    json_str = analysis_text[json_start + 7:json_end].strip()
                    analysis_data = json.loads(json_str)
                    
                    # Feedback
                    st.subheader("📝 Analysis Feedback")
                    feedback = analysis_data.get("feedback", "No feedback available.")
                    st.write(feedback)
                    
                    st.divider()
                    
                    # Improvements
                    st.subheader("🔧 Recommended Improvements")
                    improvements = analysis_data.get("improvements", [])
                    if isinstance(improvements, list):
                        for i, improvement in enumerate(improvements, 1):
                            st.write(f"{i}. {improvement}")
                    else:
                        st.write(improvements)
                
                else:
                    st.write(analysis_text)
            except (json.JSONDecodeError, ValueError):
                st.write(analysis_text)
    
    else:
        # Landing page with enhanced design
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <h1 style="font-size: 2.5rem; margin-bottom: 20px; border: none;">
                Welcome to AI Resume Analyzer! 👋
            </h1>
            <p style="font-size: 1.1rem; color: #64748b; margin-bottom: 40px;">
                Unlock your potential with AI-powered resume optimization and interview preparation
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.1) 100%);
                        padding: 25px; border-radius: 15px; border: 2px solid rgba(99,102,241,0.2); text-align: center;">
                <p style="font-size: 2.5rem; margin: 0;">📊</p>
                <h3 style="color: #6366f1; margin: 15px 0 10px 0; border: none;">Match Analysis</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin: 0;">
                    Get a detailed score and insights on how well your resume matches the job
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(139,92,246,0.1) 0%, rgba(236,72,153,0.1) 100%);
                        padding: 25px; border-radius: 15px; border: 2px solid rgba(139,92,246,0.2); text-align: center;">
                <p style="font-size: 2.5rem; margin: 0;">✨</p>
                <h3 style="color: #8b5cf6; margin: 15px 0 10px 0; border: none;">Resume Enhancement</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin: 0;">
                    Generate an AI-optimized resume tailored to the job description
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(236,72,153,0.1) 0%, rgba(245,158,11,0.1) 100%);
                        padding: 25px; border-radius: 15px; border: 2px solid rgba(236,72,153,0.2); text-align: center;">
                <p style="font-size: 2.5rem; margin: 0;">🎯</p>
                <h3 style="color: #ec4899; margin: 15px 0 10px 0; border: none;">Interview Prep</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin: 0;">
                    Get probable questions and answers from alumni interview insights
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("")
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(16,185,129,0.05) 0%, rgba(99,102,241,0.05) 100%);
                    padding: 30px; border-radius: 15px; border: 2px solid rgba(16,185,129,0.2);">
            <h3 style="color: #10b981; margin-top: 0;">🚀 Getting Started</h3>
            <ol style="color: #334155; font-size: 0.95rem; line-height: 1.8;">
                <li><strong>Upload Your Resume:</strong> Choose between text input or PDF upload in the sidebar</li>
                <li><strong>Add Job Description:</strong> Paste the job posting you're interested in</li>
                <li><strong>Analyze:</strong> Click the "🔍 Analyze" button to get instant insights</li>
                <li><strong>Review Results:</strong> Explore all 5 analysis tabs for comprehensive feedback</li>
                <li><strong>Optimize & Prepare:</strong> Generate your enhanced resume and interview guide</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(139,92,246,0.05) 100%);
                    padding: 20px; border-radius: 12px; border: 2px solid rgba(99,102,241,0.2); text-align: center;">
            <p style="color: #64748b; font-size: 0.95rem; margin: 0;">
                👈 <strong>Use the sidebar on the left</strong> to upload your resume and job description to begin!
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()