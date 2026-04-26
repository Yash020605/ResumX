"""
ResumX V2 – End-to-End Test Script
====================================
Tests all V2 endpoints against the running local server.
Run with: backend/venv/Scripts/python.exe backend/test_v2.py

Covers:
  1. Health check (Groq pool status)
  2. Agent status (LangGraph availability)
  3. Full pipeline run (all 5 agents + key rotation)
  4. Auth signup / login (requires Postgres – skipped if DB unavailable)
  5. TPO report generation (requires Postgres)
"""
import json
import sys
import time
import requests

BASE = "http://127.0.0.1:5000/api"
PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
SKIP = "\033[93m⊘\033[0m"

SAMPLE_RESUME = """
John Doe | john@example.com | github.com/johndoe
Education: B.Tech Computer Science, ADYPU, 2024, CGPA 8.2
Skills: Python, Flask, FastAPI, React, JavaScript, SQL, Git, Docker basics
Projects:
  - Student Portal: Built with Flask + React, REST API, MySQL backend
  - ML Classifier: Scikit-learn, pandas, numpy – 92% accuracy on MNIST
Experience: Python Intern @ TechCorp (3 months) – built REST APIs, wrote unit tests
"""

SAMPLE_JD = """
Backend Developer – Python
Requirements: Python, Django/FastAPI, PostgreSQL, Redis, Docker, Kubernetes,
CI/CD pipelines, AWS basics, REST API design, microservices architecture.
Nice to have: Celery, RabbitMQ, GraphQL.
"""


def section(title):
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}")


def check(label, condition, detail=""):
    icon = PASS if condition else FAIL
    print(f"  {icon}  {label}" + (f"  →  {detail}" if detail else ""))
    return condition


def post(path, body, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.post(f"{BASE}{path}", json=body, headers=headers, timeout=120)
        return r.status_code, r.json()
    except Exception as e:
        return 0, {"error": str(e)}


def get(path, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.get(f"{BASE}{path}", headers=headers, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 0, {"error": str(e)}


# ── 1. Health ─────────────────────────────────────────────────────────────────
section("1. Health Check")
code, data = get("/health")
check("HTTP 200", code == 200)
check("Status healthy", data.get("status") == "healthy")
pool = data.get("groq_pool", {})
check(f"Groq pool loaded",
      pool.get("total_keys", 0) > 0,
      f"{pool.get('active_keys', 0)}/{pool.get('total_keys', 0)} active")
db_ok = data.get("database") == "connected"
check("Database", db_ok, data.get("database", "unavailable"))


# ── 2. Agent Status ───────────────────────────────────────────────────────────
section("2. LangGraph Agent Status")
code, data = get("/agents/status")
check("HTTP 200", code == 200)
check("LangGraph available", data.get("available") is True,
      f"v{data.get('langgraph_version', '?')}")
check("LangChain available", "langchain_version" in data,
      f"v{data.get('langchain_version', '?')}")


# ── 3. Full Pipeline ──────────────────────────────────────────────────────────
section("3. Full Agent Pipeline (all 5 agents)")
print("  ⏳ Running pipeline – this takes ~30-60s with Groq pool rotation...")
t0 = time.time()
code, data = post("/agents/run", {
    "resume": SAMPLE_RESUME,
    "job_description": SAMPLE_JD,
})
elapsed = time.time() - t0

check("HTTP 200", code == 200, f"got {code}")
if code == 200:
    check("match_percentage present",
          data.get("match_percentage") is not None,
          str(data.get("match_percentage")) + "%")
    check("skill_gaps returned",
          isinstance(data.get("skill_gaps"), list),
          str(len(data.get("skill_gaps", []))) + " gaps")
    check("career_fields returned",
          len(data.get("career_fields", [])) > 0,
          str(len(data.get("career_fields", []))) + " fields")
    check("improved_resume present",
          bool(data.get("improved_resume")))
    check("suggested_projects present",
          len(data.get("suggested_projects", [])) > 0,
          str(len(data.get("suggested_projects", []))) + " projects")
    check("interview_questions present",
          len(data.get("interview_questions", [])) > 0,
          str(len(data.get("interview_questions", []))) + " questions")
    completed = data.get("completed_agents", [])
    check("All 5 agents completed",
          len(completed) >= 5,
          str(completed))
    check(f"Pipeline time", True, f"{elapsed:.1f}s")
else:
    print(f"  {FAIL}  Pipeline error: {data.get('error', data)}")


# ── 4. Auth (requires Postgres) ───────────────────────────────────────────────
section("4. Auth – Signup / Login")
if not db_ok:
    print(f"  {SKIP}  Skipped – Postgres not running")
    print(f"         Start with: docker run -d --name resumx-db \\")
    print(f"           -e POSTGRES_USER=resumx -e POSTGRES_PASSWORD=resumx \\")
    print(f"           -e POSTGRES_DB=resumx_db -p 5432:5432 postgres:16")
    access_token = None
else:
    # Create org first (direct DB insert would be needed in real setup)
    code, data = post("/auth/signup", {
        "email":      "test.student@adypu.edu.in",
        "password":   "Test@1234",
        "full_name":  "Test Student",
        "org_domain": "adypu.edu.in",
        "role":       "student",
    })
    check("Signup 201 or 409", code in (201, 409), f"got {code}")
    access_token = data.get("access_token")

    if code == 409:
        code, data = post("/auth/login", {
            "email":    "test.student@adypu.edu.in",
            "password": "Test@1234",
        })
        check("Login 200", code == 200, f"got {code}")
        access_token = data.get("access_token")

    check("Access token received", bool(access_token))


# ── 5. TPO Report (requires Postgres) ────────────────────────────────────────
section("5. TPO Batch Report")
if not db_ok:
    print(f"  {SKIP}  Skipped – Postgres not running")
else:
    if access_token:
        code, data = get("/tpo/report", token=access_token)
        check("TPO report endpoint reachable", code in (200, 403, 404),
              f"HTTP {code}")
    else:
        print(f"  {SKIP}  Skipped – no auth token")


# ── 6. Key Manager stress hint ────────────────────────────────────────────────
section("6. Key Pool Summary")
code, data = get("/health")
pool = data.get("groq_pool", {})
print(f"  Total keys   : {pool.get('total_keys', '?')}")
print(f"  Active keys  : {pool.get('active_keys', '?')}")
print(f"  Blacklisted  : {pool.get('blacklisted_keys', '?')}")
print(f"  Blacklist TTL: 60s (configurable via GROQ_BLACKLIST_TTL)")


# ── Summary ───────────────────────────────────────────────────────────────────
section("Done")
print("  Backend  → http://127.0.0.1:5000")
print("  Frontend → http://localhost:3000")
print("  Health   → http://127.0.0.1:5000/api/health")
print()
