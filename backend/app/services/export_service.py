"""
Export Service – Recruiter Match & ZIP Export
==============================================

Responsibilities:
  1. match_resumes_to_jd()  – vector similarity search of all org resumes vs a JD
  2. build_resume_zip()     – generate a ZIP of top-N matched student resume texts
  3. All exports are logged to AnalysisLogs for privacy auditing

Vector search strategy:
  - Uses sentence-transformers (all-MiniLM-L6-v2) if available (same as RAGStore)
  - Falls back to TF-IDF cosine similarity via sklearn if available
  - Final fallback: keyword overlap scoring (always available, no deps)
"""
from __future__ import annotations

import io
import zipfile
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.db.models import AgentSession, AnalysisLog, User


# ── Similarity backends ───────────────────────────────────────────────────────

def _cosine_similarity_np(a, b) -> float:
    """Cosine similarity between two numpy vectors."""
    import numpy as np
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0


def _embed_texts(texts: List[str]) -> Optional[list]:
    """Try sentence-transformers first, then sklearn TF-IDF."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(texts, convert_to_numpy=True)
    except Exception:
        pass

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer(max_features=5000, stop_words="english")
        return vec.fit_transform(texts).toarray()
    except Exception:
        pass

    return None


def _keyword_score(resume: str, jd: str) -> float:
    """Fallback: Jaccard similarity on word sets."""
    r_words = set(resume.lower().split())
    j_words = set(jd.lower().split())
    if not j_words:
        return 0.0
    return len(r_words & j_words) / len(j_words)


# ── Core matching logic ───────────────────────────────────────────────────────

def match_resumes_to_jd(
    db: Session,
    org_id: str,
    job_description: str,
    top_n: int = 50,
) -> List[Tuple[str, str, float]]:
    """
    Runs a vector similarity search comparing the JD against all student
    resumes in the org.

    Returns a sorted list of (user_id, full_name, score) tuples,
    highest score first, capped at top_n.
    """
    users = db.query(User).filter_by(
        org_id=org_id, is_active=True, role="student"
    ).all()

    # Collect users who have a resume
    candidates = []
    for user in users:
        resume_text = user.resume_text or ""
        if not resume_text.strip():
            # Try to pull from latest agent session state
            session = (
                db.query(AgentSession)
                .filter_by(user_id=user.id)
                .order_by(AgentSession.updated_at.desc())
                .first()
            )
            if session and session.agent_state:
                resume_text = session.agent_state.get("resume_raw", "")

        if resume_text.strip():
            candidates.append((user.id, user.full_name or user.email, resume_text))

    if not candidates:
        return []

    user_ids   = [c[0] for c in candidates]
    names      = [c[1] for c in candidates]
    resumes    = [c[2] for c in candidates]

    # Build corpus: JD first, then all resumes
    corpus = [job_description] + resumes
    embeddings = _embed_texts(corpus)

    if embeddings is not None:
        import numpy as np
        jd_vec = embeddings[0]
        resume_vecs = embeddings[1:]
        scores = [_cosine_similarity_np(jd_vec, rv) for rv in resume_vecs]
    else:
        # Pure keyword fallback
        scores = [_keyword_score(r, job_description) for r in resumes]

    # Sort by score descending, take top_n
    ranked = sorted(
        zip(user_ids, names, scores),
        key=lambda x: x[2],
        reverse=True,
    )
    return ranked[:top_n]


def build_resume_zip(
    db: Session,
    org_id: str,
    job_description: str,
    requested_by_user_id: str,
    top_n: int = 50,
) -> Tuple[bytes, List[dict]]:
    """
    Matches resumes to the JD, packages the top-N as a ZIP of .txt files,
    and logs the export event to AnalysisLogs for privacy auditing.

    Returns:
      (zip_bytes, manifest)  where manifest is a list of matched student dicts
    """
    matches = match_resumes_to_jd(db, org_id, job_description, top_n)

    zip_buffer = io.BytesIO()
    manifest = []

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Write a manifest CSV inside the ZIP
        manifest_lines = ["rank,student_name,match_score\n"]

        for rank, (user_id, name, score) in enumerate(matches, start=1):
            # Fetch resume text
            user = db.query(User).filter_by(id=user_id).first()
            resume_text = (user.resume_text or "") if user else ""

            if not resume_text:
                session = (
                    db.query(AgentSession)
                    .filter_by(user_id=user_id)
                    .order_by(AgentSession.updated_at.desc())
                    .first()
                )
                if session and session.agent_state:
                    resume_text = session.agent_state.get("resume_raw", "")

            safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
            filename = f"{rank:02d}_{safe_name}_{int(score * 100)}pct.txt"
            zf.writestr(filename, resume_text or "(No resume text available)")

            manifest_lines.append(f"{rank},{name},{score:.3f}\n")
            manifest.append({"rank": rank, "student_name": name, "match_score": round(score, 3)})

        zf.writestr("_manifest.csv", "".join(manifest_lines))

    # Privacy audit log – one entry per export event
    audit_log = AnalysisLog(
        org_id=org_id,
        student_id=requested_by_user_id,
        model_used="recruiter_match_export",
        match_score=float(len(matches)),   # store count as score for audit
        timestamp=datetime.now(timezone.utc),
    )
    db.add(audit_log)
    db.commit()

    return zip_buffer.getvalue(), manifest
