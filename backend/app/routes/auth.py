"""
ResumX V2 – Auth Routes
========================
Works in two modes:
  - DB mode   : Postgres is running → full persistence
  - Local mode: No Postgres → in-memory store (survives server restarts via JSON file)

POST /api/auth/signup
POST /api/auth/login
POST /api/auth/refresh
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

import bcrypt
from flask import Blueprint, jsonify, request

from app.core.auth import create_access_token, create_refresh_token, decode_token
from app.utils.validators import InputValidator

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ── Local fallback store (JSON file next to .env) ─────────────────────────────
_LOCAL_STORE_PATH = Path(__file__).parent.parent.parent / "local_users.json"


def _load_local() -> dict:
    try:
        return json.loads(_LOCAL_STORE_PATH.read_text())
    except Exception:
        return {"users": {}, "orgs": {}}


def _save_local(data: dict) -> None:
    _LOCAL_STORE_PATH.write_text(json.dumps(data, indent=2))


def _db_available() -> bool:
    try:
        from app.db.session import engine
        import sqlalchemy
        with engine.connect() as c:
            c.execute(sqlalchemy.text("SELECT 1"))
        return True
    except Exception:
        return False


# ── Signup ────────────────────────────────────────────────────────────────────

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data      = request.get_json() or {}

    # OWASP: Validate and reject unexpected fields (mass-assignment protection)
    ok, err = InputValidator.validate_auth_signup(data)
    if not ok:
        return jsonify({"error": err}), 400

    email     = str(data.get("email", "")).strip().lower()
    password  = str(data.get("password", ""))
    full_name = str(data.get("full_name", "")).strip()
    org_domain = str(data.get("org_domain", "")).strip().lower()
    role      = str(data.get("role", "student"))

    # ── DB mode ───────────────────────────────────────────────────────────────
    if _db_available():
        try:
            from app.db.models import Organization, User
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                org = db.query(Organization).filter_by(domain=org_domain, is_active=True).first()
                if not org:
                    # Auto-create org if not found (dev convenience)
                    org = Organization(
                        name=org_domain.split(".")[0].upper(),
                        domain=org_domain,
                    )
                    db.add(org); db.commit(); db.refresh(org)

                if db.query(User).filter_by(email=email).first():
                    return jsonify({"error": "Email already registered"}), 409

                pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                user = User(org_id=org.id, email=email, password_hash=pw_hash,
                            full_name=full_name, role=role)
                db.add(user); db.commit(); db.refresh(user)

                access  = create_access_token(user.id, str(org.id), user.role)
                refresh = create_refresh_token(user.id)
                return jsonify({
                    "access_token": access, "refresh_token": refresh,
                    "user": {"id": user.id, "email": user.email,
                             "role": user.role, "org": org.name},
                }), 201
            finally:
                db.close()
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # ── Local mode (no Postgres) ──────────────────────────────────────────────
    store = _load_local()
    if email in store["users"]:
        return jsonify({"error": "Email already registered"}), 409

    # Auto-create org entry
    if org_domain not in store["orgs"]:
        store["orgs"][org_domain] = {
            "id":   str(uuid.uuid4()),
            "name": org_domain.split(".")[0].upper(),
            "domain": org_domain,
            "dream_companies": [],
        }
    org = store["orgs"][org_domain]

    user_id = str(uuid.uuid4())
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    store["users"][email] = {
        "id":            user_id,
        "email":         email,
        "password_hash": pw_hash,
        "full_name":     full_name,
        "role":          role,
        "org_id":        org["id"],
        "org_domain":    org_domain,
        "org_name":      org["name"],
    }
    _save_local(store)

    access  = create_access_token(user_id, org["id"], role)
    refresh = create_refresh_token(user_id)
    return jsonify({
        "access_token": access, "refresh_token": refresh,
        "user": {"id": user_id, "email": email,
                 "role": role, "org": org["name"]},
    }), 201


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json() or {}

    # OWASP: Validate login payload and reject unexpected fields
    ok, err = InputValidator.validate_auth_login(data)
    if not ok:
        return jsonify({"error": err}), 400

    email    = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    # ── DB mode ───────────────────────────────────────────────────────────────
    if _db_available():
        try:
            from app.db.models import AgentSession, User
            from app.db.session import SessionLocal
            from datetime import datetime, timezone
            db = SessionLocal()
            try:
                user = db.query(User).filter_by(email=email, is_active=True).first()
                if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                    return jsonify({"error": "Invalid credentials"}), 401
                user.last_login = datetime.now(timezone.utc)
                db.commit()
                latest = (db.query(AgentSession)
                          .filter_by(user_id=user.id, status="active")
                          .order_by(AgentSession.updated_at.desc()).first())
                access  = create_access_token(user.id, str(user.org_id), user.role)
                refresh = create_refresh_token(user.id)
                return jsonify({
                    "access_token": access, "refresh_token": refresh,
                    "user": {"id": user.id, "email": user.email,
                             "role": user.role, "org_id": str(user.org_id)},
                    "resume_session": {
                        "session_id": latest.id if latest else None,
                        "last_node":  latest.last_node if latest else None,
                    },
                })
            finally:
                db.close()
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # ── Local mode ────────────────────────────────────────────────────────────
    store = _load_local()
    u = store["users"].get(email)
    if not u or not bcrypt.checkpw(password.encode(), u["password_hash"].encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    access  = create_access_token(u["id"], u["org_id"], u["role"])
    refresh = create_refresh_token(u["id"])
    return jsonify({
        "access_token": access, "refresh_token": refresh,
        "user": {"id": u["id"], "email": u["email"],
                 "role": u["role"], "org_id": u["org_id"],
                 "org": u.get("org_name", "")},
        "resume_session": {"session_id": None, "last_node": None},
    })


# ── Refresh ───────────────────────────────────────────────────────────────────

@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    data    = request.get_json() or {}
    token   = (data.get("refresh_token") or "").strip()
    payload = decode_token(token)

    if not payload or payload.get("type") != "refresh":
        return jsonify({"error": "Invalid or expired refresh token"}), 401

    user_id = payload["sub"]

    # Try DB first
    if _db_available():
        try:
            from app.db.models import User
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                user = db.query(User).filter_by(id=user_id, is_active=True).first()
                if not user:
                    return jsonify({"error": "User not found"}), 404
                access = create_access_token(user.id, str(user.org_id), user.role)
                return jsonify({"access_token": access})
            finally:
                db.close()
        except Exception:
            pass

    # Local mode fallback
    store = _load_local()
    for u in store["users"].values():
        if u["id"] == user_id:
            access = create_access_token(u["id"], u["org_id"], u["role"])
            return jsonify({"access_token": access})

    return jsonify({"error": "User not found"}), 404
