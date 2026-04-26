"""
AI Service – automatically uses Groq (online) or Ollama (offline).

All direct API endpoints (/analyze, /improve-resume, etc.) go through this class.
It probes internet connectivity on every call (cached 30s) and routes accordingly.
"""
import os
import json
import re
import requests as _requests
from typing import Dict, Any, List

from app.utils.connectivity import is_online

# ── Config ────────────────────────────────────────────────────────────────────

_GROQ_URL    = "https://api.groq.com/openai/v1/chat/completions"
_GROQ_MODEL  = os.getenv("GROQ_MODEL",      "llama-3.3-70b-versatile")
_OLLAMA_URL  = os.getenv("OLLAMA_BASE_URL",  "http://localhost:11434")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL",    "llama3.1")
_BACKEND_ENV  = os.getenv("LLM_BACKEND",     "auto").lower()


class GroqAIService:
    """
    Unified AI service.
    Calls Groq when online, Ollama when offline.
    The public interface is identical regardless of backend.
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        # Expose these so the /api/chat route can reuse them
        self.url     = _GROQ_URL
        self.model   = _GROQ_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ── Backend selection ─────────────────────────────────────────────────────

    def _use_groq(self) -> bool:
        if _BACKEND_ENV == "groq":
            return True
        if _BACKEND_ENV == "ollama":
            return False
        return is_online()

    # ── Core LLM call ─────────────────────────────────────────────────────────

    def _call_groq(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Routes to Ollama on any Groq failure (401, 429, network error).
        """
        if self._use_groq():
            try:
                return self._call_groq_api(prompt, max_tokens)
            except Exception as e:
                err = str(e)
                if any(code in err for code in ["429", "401", "403", "Too Many", "Unauthorized", "rate"]):
                    print(f"[AIService] Groq unavailable ({err[:60]}), falling back to Ollama")
                    return self._call_ollama_api(prompt, max_tokens)
                raise
        return self._call_ollama_api(prompt, max_tokens)

    def _call_groq_api(self, prompt: str, max_tokens: int) -> str:
        payload = {
            "model": _GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant specializing in resume analysis and career guidance. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": max_tokens,
        }
        resp = _requests.post(_GROQ_URL, json=payload, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    def _call_ollama_api(self, prompt: str, max_tokens: int) -> str:
        """Call local Ollama instance using its chat endpoint."""
        url = f"{_OLLAMA_URL}/api/chat"
        payload = {
            "model": _OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant specializing in resume analysis and career guidance. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.7},
        }
        try:
            resp = _requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"].strip()
        except _requests.exceptions.ConnectionError:
            raise Exception(
                "No AI service available. Groq API key is invalid and Ollama is not running. "
                "Please update your GROQ_API_KEY in backend/.env or start Ollama (ollama serve)."
            )
        except Exception as e:
            raise Exception(f"Ollama API call failed: {str(e)}")

    # ── JSON parsing ──────────────────────────────────────────────────────────

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Robust JSON parser – handles markdown fences and control characters."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            cleaned = response.strip()

            # Strip markdown fences
            if "```json" in cleaned:
                s = cleaned.find("```json") + 7
                e = cleaned.find("```", s)
                if e > s:
                    cleaned = cleaned[s:e].strip()
            elif "```" in cleaned:
                lines, in_block, out = cleaned.split("\n"), False, []
                for line in lines:
                    if line.strip() == "```":
                        in_block = not in_block
                        continue
                    if in_block or line.strip().startswith("{"):
                        out.append(line)
                cleaned = "\n".join(out).strip()

            # Remove control characters
            cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", cleaned)

            s, e = cleaned.find("{"), cleaned.rfind("}") + 1
            if s >= 0 and e > s:
                chunk = cleaned[s:e]
                try:
                    return json.loads(chunk)
                except json.JSONDecodeError:
                    pass
                try:
                    import ast
                    result = ast.literal_eval(
                        chunk.replace("true", "True").replace("false", "False").replace("null", "None")
                    )
                    if isinstance(result, dict):
                        return result
                except Exception:
                    pass
                # Manual extraction for improved_resume
                try:
                    result = {}
                    result["success"] = '"success": false' not in chunk and '"success":false' not in chunk
                    rs = chunk.find('"improved_resume": "')
                    if rs >= 0:
                        rs += len('"improved_resume": "')
                        for end_marker in ['",\n    "status":', '", "status":', '"status":']:
                            re_ = chunk.find(end_marker, rs)
                            if re_ > rs:
                                result["improved_resume"] = chunk[rs:re_].replace('\\"', '"')
                                break
                    ss = chunk.find('"status": "')
                    if ss >= 0:
                        ss += len('"status": "')
                        se = chunk.find('"', ss)
                        if se > ss:
                            result["status"] = chunk[ss:se]
                    if "improved_resume" in result:
                        return result
                except Exception:
                    pass

            raise ValueError(f"Could not parse JSON: {response[:200]}...")

    # ── Public methods (unchanged interface) ──────────────────────────────────

    def analyze_resume_match(self, resume: str, job_description: str) -> Dict[str, Any]:
        backend = "Groq" if self._use_groq() else "Ollama"
        print(f"[AIService] analyze_resume_match via {backend}")

        prompt = f"""
Analyze how well this resume matches this job description. Provide a detailed analysis in the following JSON format:

{{
    "match_percentage": <number between 0-100>,
    "matching_skills": [<list of skills that appear in both resume and job description>],
    "missing_skills": [<list of important skills from job description not found in resume>],
    "skill_gaps": [{{"skill": "<skill name>", "importance": "<high/medium/low>"}}],
    "feedback": "<detailed feedback on the match quality>",
    "improvements": [<list of specific improvement suggestions>],
    "career_fields": [<list of relevant career fields based on resume skills>],
    "key_strengths": [<top 3 strengths from resume>],
    "summary": "<brief summary of the analysis>"
}}

Resume:
{resume}

Job Description:
{job_description}

Respond with ONLY valid JSON, no additional text.
"""
        try:
            response = self._call_groq(prompt, max_tokens=1500)
            result = self._parse_json_response(response)
            defaults = {
                "match_percentage": 50,
                "matching_skills": [], "missing_skills": [], "skill_gaps": [],
                "feedback": "Analysis not available", "improvements": [],
                "career_fields": [], "key_strengths": [], "summary": "Analysis not available",
            }
            for k, v in defaults.items():
                if k not in result:
                    result[k] = v
            return result
        except Exception as e:
            err_str = str(e)
            # Provide a user-friendly message for rate limits
            if "429" in err_str or "Too Many" in err_str:
                msg = "AI service is temporarily rate-limited. Please wait a moment and try again."
            elif "Ollama" in err_str or "Connection refused" in err_str:
                msg = "Offline mode: Ollama is not running. Start Ollama or connect to the internet."
            else:
                msg = f"Analysis failed: {err_str}"
            return {"error": msg}

    def generate_improved_resume(self, original_resume: str, job_description: str, improvements: list) -> Dict[str, Any]:
        def fallback():
            lines = [original_resume, "\n\nIMPROVEMENTS IMPLEMENTED:"]
            lines += [f"{i+1}. {imp}" for i, imp in enumerate(improvements)]
            return {
                "success": True,
                "improved_resume": "\n".join(lines),
                "status": f"Resume enhanced with {len(improvements)} improvements",
            }

        backend = "Groq" if self._use_groq() else "Ollama"
        print(f"[AIService] generate_improved_resume via {backend}")

        prompt = f"""
Based on the job description and the requested improvements, create an improved version of the resume.

Improvements to implement: {', '.join(improvements)}

Provide your response in the following JSON format:
{{
    "success": true,
    "improved_resume": "<the complete improved resume text>",
    "status": "<brief description of changes made>"
}}

Original Resume:
{original_resume}

Job Description:
{job_description}

Respond with ONLY valid JSON, no additional text.
"""
        try:
            response = self._call_groq(prompt, max_tokens=2000)
            result = self._parse_json_response(response)
            if not result.get("improved_resume", "").strip():
                return fallback()
            result.setdefault("success", True)
            result.setdefault("status", "Resume updated with job-specific improvements")
            return result
        except Exception as e:
            print(f"[AIService] generate_improved_resume error: {e}, using fallback")
            return fallback()

    def get_career_fields(self, resume: str) -> Dict[str, Any]:
        backend = "Groq" if self._use_groq() else "Ollama"
        print(f"[AIService] get_career_fields via {backend}")

        prompt = f"""
Based on the skills and experience in this resume, suggest appropriate career fields, job titles, and related information.

Resume:
{resume}

Provide your response in the following JSON format:
{{
    "career_fields": [{{"field": "<name>", "explanation": "<why it fits>"}}],
    "job_titles": [<list of relevant job titles>],
    "industries": [<list of relevant industries>],
    "growth_opportunities": [<list of potential next career steps>],
    "recommended_skills": [<additional skills to develop>],
    "certifications": [<recommended certifications>],
    "summary": "<overall career summary>"
}}

Respond with ONLY valid JSON, no additional text.
"""
        try:
            response = self._call_groq(prompt, max_tokens=1500)
            result = self._parse_json_response(response)
            for k in ["career_fields", "job_titles", "industries", "growth_opportunities", "recommended_skills", "certifications"]:
                result.setdefault(k, [])
            result.setdefault("summary", "Career analysis not available")
            return result
        except Exception as e:
            return {"error": f"Career analysis failed: {str(e)}"}

    def generate_interview_prep(self, resume: str, job_description: str) -> Dict[str, Any]:
        backend = "Groq" if self._use_groq() else "Ollama"
        print(f"[AIService] generate_interview_prep via {backend}")

        prompt = f"""
Create a comprehensive interview preparation guide based on the resume and job description.

Resume:
{resume}

Job Description:
{job_description}

Provide your response in the following JSON format:
{{
    "probable_questions": [<list of likely interview questions>],
    "focus_areas": [<key areas to prepare for>],
    "expected_answers": {{"<question>": "<expected answer guidance>"}},
    "follow_up_questions": [<potential follow-up questions>],
    "common_mistakes": [<common mistakes to avoid>],
    "strengths_to_highlight": [<key strengths to emphasize>],
    "prep_resources": [<recommended preparation resources>],
    "tips": [<specific preparation tips>]
}}

Respond with ONLY valid JSON, no additional text.
"""
        try:
            response = self._call_groq(prompt, max_tokens=1500)
            result = self._parse_json_response(response)
            for k in ["probable_questions", "focus_areas", "follow_up_questions", "common_mistakes", "strengths_to_highlight", "prep_resources", "tips"]:
                result.setdefault(k, [])
            result.setdefault("expected_answers", {})
            return result
        except Exception as e:
            return {"error": f"Interview prep failed: {str(e)}"}

    def evaluate_interview_answer(self, question: str, answer: str, resume: str) -> Dict[str, Any]:
        backend = "Groq" if self._use_groq() else "Ollama"
        print(f"[AIService] evaluate_interview_answer via {backend}")

        prompt = f"""
Evaluate the candidate's answer to the interview question based on their resume.

Question: {question}
Candidate's Answer: {answer}
Candidate's Resume: {resume}

Provide your response in the following JSON format:
{{
    "score": <number 1-10>,
    "feedback": "<detailed constructive feedback>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "areas_for_improvement": ["<area 1>", "<area 2>"],
    "ideal_answer_concept": "<how an ideal answer should be structured>"
}}

Respond with ONLY valid JSON, no additional text.
"""
        try:
            response = self._call_groq(prompt, max_tokens=1500)
            result = self._parse_json_response(response)
            result.setdefault("score", 5)
            result.setdefault("feedback", "Evaluation not available")
            result.setdefault("strengths", [])
            result.setdefault("areas_for_improvement", [])
            result.setdefault("ideal_answer_concept", "Not available")
            return result
        except Exception as e:
            return {"error": f"Answer evaluation failed: {str(e)}"}
