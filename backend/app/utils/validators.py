"""
OWASP Input Validation & Sanitization
======================================
- Schema-based validation with type checks and length limits
- Rejects unexpected fields (allowlist approach)
- Strips dangerous characters from string inputs
- All validators return (is_valid: bool, error_message: str)
"""
from __future__ import annotations
import re
import html
from typing import Any, Dict, Tuple

# ── Constants ─────────────────────────────────────────────────────────────────
MIN_RESUME_LEN      = 50
MAX_RESUME_LEN      = 50_000
MIN_JD_LEN          = 30
MAX_JD_LEN          = 10_000
MAX_EMAIL_LEN       = 320
MAX_PASSWORD_LEN    = 128
MIN_PASSWORD_LEN    = 8
MAX_NAME_LEN        = 255
MAX_DOMAIN_LEN      = 253
MAX_SESSION_CODE_LEN = 20

# Allowlist: only these fields are accepted in auth payloads
AUTH_SIGNUP_FIELDS  = {"email", "password", "full_name", "org_domain", "role"}
AUTH_LOGIN_FIELDS   = {"email", "password"}

# Dangerous patterns to strip from free-text inputs (XSS / injection)
_DANGEROUS_PATTERN = re.compile(r"[<>\"'`;]")

def _sanitize(text: str) -> str:
    """Strip HTML-dangerous characters and normalize whitespace."""
    # HTML-escape then strip residual dangerous chars
    cleaned = html.escape(str(text), quote=True)
    cleaned = _DANGEROUS_PATTERN.sub("", cleaned)
    return cleaned.strip()

def _check_unexpected_fields(data: dict, allowed: set) -> Tuple[bool, str]:
    """Reject payloads containing fields not in the allowlist (OWASP mass-assignment)."""
    unexpected = set(data.keys()) - allowed
    if unexpected:
        return False, f"Unexpected fields: {', '.join(sorted(unexpected))}"
    return True, ""


class InputValidator:

    MIN_RESUME_LENGTH   = MIN_RESUME_LEN
    MAX_RESUME_LENGTH   = MAX_RESUME_LEN
    MIN_JOB_DESC_LENGTH = MIN_JD_LEN
    MAX_JOB_DESC_LENGTH = MAX_JD_LEN

    @staticmethod
    def validate_resume(resume: str) -> Tuple[bool, str]:
        if not isinstance(resume, str):
            return False, "Resume must be a string"
        resume = resume.strip()
        if len(resume) < MIN_RESUME_LEN:
            return False, f"Resume must be at least {MIN_RESUME_LEN} characters"
        if len(resume) > MAX_RESUME_LEN:
            return False, f"Resume cannot exceed {MAX_RESUME_LEN} characters"
        return True, ""

    @staticmethod
    def validate_job_description(job_desc: str) -> Tuple[bool, str]:
        if not isinstance(job_desc, str):
            return False, "Job description must be a string"
        job_desc = job_desc.strip()
        if len(job_desc) < MIN_JD_LEN:
            return False, f"Job description must be at least {MIN_JD_LEN} characters"
        if len(job_desc) > MAX_JD_LEN:
            return False, f"Job description cannot exceed {MAX_JD_LEN} characters"
        return True, ""

    @staticmethod
    def validate_both(resume: str, job_desc: str) -> Tuple[bool, str]:
        ok, err = InputValidator.validate_resume(resume)
        if not ok:
            return False, err
        return InputValidator.validate_job_description(job_desc)

    @staticmethod
    def validate_auth_signup(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate and sanitize signup payload."""
        # Reject unexpected fields
        ok, err = _check_unexpected_fields(data, AUTH_SIGNUP_FIELDS)
        if not ok:
            return False, err

        email    = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        name     = str(data.get("full_name", "")).strip()
        domain   = str(data.get("org_domain", "")).strip().lower()
        role     = str(data.get("role", "student"))

        # Email
        if not email or len(email) > MAX_EMAIL_LEN:
            return False, "Invalid email address"
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return False, "Invalid email format"

        # Password
        if len(password) < MIN_PASSWORD_LEN:
            return False, f"Password must be at least {MIN_PASSWORD_LEN} characters"
        if len(password) > MAX_PASSWORD_LEN:
            return False, "Password too long"

        # Full name
        if name and len(name) > MAX_NAME_LEN:
            return False, "Name too long"

        # Org domain
        if not domain or len(domain) > MAX_DOMAIN_LEN:
            return False, "Invalid organisation domain"
        if not re.match(r"^[a-z0-9][a-z0-9\-\.]+\.[a-z]{2,}$", domain):
            return False, "Invalid domain format (e.g. college.edu.in)"

        # Role
        if role not in ("student", "tpo"):
            return False, "role must be 'student' or 'tpo'"

        return True, ""

    @staticmethod
    def validate_auth_login(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate login payload."""
        ok, err = _check_unexpected_fields(data, AUTH_LOGIN_FIELDS)
        if not ok:
            return False, err

        email    = str(data.get("email", "")).strip()
        password = str(data.get("password", ""))

        if not email or not password:
            return False, "email and password are required"
        if len(email) > MAX_EMAIL_LEN:
            return False, "Invalid email"
        if len(password) > MAX_PASSWORD_LEN:
            return False, "Invalid password"
        return True, ""

    @staticmethod
    def validate_session_code(code: str) -> Tuple[bool, str]:
        """Validate TPO session code format."""
        if not isinstance(code, str):
            return False, "session_code must be a string"
        code = code.strip()
        if not code or len(code) > MAX_SESSION_CODE_LEN:
            return False, "Invalid session code"
        if not re.match(r"^[A-Z0-9]{1,6}-\d{4}-[A-Z0-9]{2}$", code):
            return False, "Invalid session code format"
        return True, ""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize free-text input for safe storage/display."""
        return _sanitize(text)
