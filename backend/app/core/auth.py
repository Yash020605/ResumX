"""
ResumX V2 – JWT Authentication Helpers
=======================================
Provides sign/verify for access tokens and a Flask decorator for
protecting routes by role (student | tpo | admin).

JWT_SECRET must be set in .env.
"""
from __future__ import annotations

import os
import warnings
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional

import jwt
from flask import jsonify, request

JWT_SECRET    = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"

# OWASP: Warn loudly at startup if the default insecure secret is still in use
if JWT_SECRET == "change-me-in-production":
    warnings.warn(
        "[SECURITY] JWT_SECRET is using the default insecure value. "
        "Set a strong random secret in your .env file before deploying.",
        stacklevel=2
    )
ACCESS_TTL    = int(os.getenv("JWT_ACCESS_TTL_MINUTES", "60"))   # minutes
REFRESH_TTL   = int(os.getenv("JWT_REFRESH_TTL_DAYS",   "30"))   # days


def create_access_token(user_id: str, org_id: str, role: str) -> str:
    payload = {
        "sub":    user_id,
        "org_id": org_id,
        "role":   role,
        "exp":    datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TTL),
        "iat":    datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub":  user_id,
        "type": "refresh",
        "exp":  datetime.now(timezone.utc) + timedelta(days=REFRESH_TTL),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(*allowed_roles: str):
    """
    Flask route decorator.
    Usage:
        @require_auth("student", "tpo")
        def my_route(): ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid Authorization header"}), 401

            token = auth_header.split(" ", 1)[1]
            payload = decode_token(token)
            if not payload:
                return jsonify({"error": "Token expired or invalid"}), 401

            if allowed_roles and payload.get("role") not in allowed_roles:
                return jsonify({"error": "Insufficient permissions"}), 403

            # Inject identity into request context
            request.user_id = payload["sub"]
            request.org_id  = payload.get("org_id")
            request.role    = payload.get("role")
            return fn(*args, **kwargs)
        return wrapper
    return decorator
