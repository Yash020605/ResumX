"""
ResumX V2 – SQLAlchemy Multi-Tenant Schema
==========================================

Tables:
  organizations  – colleges / institutions (B2B tenants)
  users          – students linked to an org, with JWT auth
  agent_sessions – persisted LangGraph AgentState per user session
  tpo_reports    – cached batch readiness reports per org
  analysis_logs  – per-run audit trail for the analytics counter

Design decisions:
  - Every user row carries an org_id FK → strict tenant isolation
  - agent_state is stored as JSONB (Postgres) for flexible schema evolution
  - dream_companies is a JSONB array on Organization for Career Agent tuning
  - Soft-delete via is_active flags (no hard deletes for audit trail)
  - total_resumes_analyzed on Organization is incremented atomically via F()
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint, JSON,
)
from sqlalchemy.orm import DeclarativeBase, relationship


# ── Base ──────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


# ── Organization (B2B Tenant) ─────────────────────────────────────────────────

class Organization(Base):
    """
    Represents a college / placement cell.
    One org → many users (students + TPOs).
    """
    __tablename__ = "organizations"

    id            = Column(String(36), primary_key=True, default=_uuid)
    name          = Column(String(255), nullable=False)          # e.g. "ADYPU"
    domain        = Column(String(255), unique=True, nullable=False)  # e.g. "adypu.edu.in"
    city          = Column(String(100))
    state         = Column(String(100))
    country       = Column(String(100), default="India")

    # TPO-configurable list of target companies for Career Agent tuning
    # e.g. ["Google", "Infosys", "TCS", "Persistent Systems"]
    dream_companies = Column(JSON, default=list)

    # Analytics counter – atomically incremented on every successful analyzer run
    total_resumes_analyzed = Column(Integer, default=0, nullable=False)

    # Subscription tier: "free" | "pro" | "enterprise"
    plan          = Column(String(50), default="free")
    is_active     = Column(Boolean, default=True)

    created_at    = Column(DateTime(timezone=True), default=_now)
    updated_at    = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    # Relationships
    users         = relationship("User", back_populates="organization", lazy="dynamic")
    tpo_reports   = relationship("TPOReport", back_populates="organization", lazy="dynamic")
    analysis_logs = relationship("AnalysisLog", back_populates="organization", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Organization {self.name} ({self.domain})>"


# ── User ──────────────────────────────────────────────────────────────────────

class User(Base):
    """
    Student or TPO account.
    role: "student" | "tpo" | "admin"
    """
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
    )

    id            = Column(String(36), primary_key=True, default=_uuid)
    org_id        = Column(String(36), ForeignKey("organizations.id",
                           ondelete="CASCADE"), nullable=False, index=True)

    email         = Column(String(320), nullable=False)
    password_hash = Column(String(256), nullable=False)
    full_name     = Column(String(255))
    role          = Column(String(20), default="student")   # student | tpo | admin

    # Cached resume text (updated on every improvement cycle)
    resume_text   = Column(Text)

    is_active     = Column(Boolean, default=True)
    last_login    = Column(DateTime(timezone=True))
    created_at    = Column(DateTime(timezone=True), default=_now)
    updated_at    = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    # Relationships
    organization  = relationship("Organization", back_populates="users")
    sessions      = relationship("AgentSession", back_populates="user",
                                 cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.role}]>"


# ── AgentSession (Persisted LangGraph State) ──────────────────────────────────

class AgentSession(Base):
    """
    Persists the full LangGraph AgentState after every node transition.
    Users can resume their career journey from any device.

    status: "active" | "completed" | "abandoned"
    """
    __tablename__ = "agent_sessions"

    id            = Column(String(36), primary_key=True, default=_uuid)
    user_id       = Column(String(36), ForeignKey("users.id",
                           ondelete="CASCADE"), nullable=False, index=True)
    org_id        = Column(String(36), ForeignKey("organizations.id",
                           ondelete="CASCADE"), nullable=False, index=True)

    # Snapshot of the full AgentState dict (JSONB for Postgres, JSON fallback)
    agent_state   = Column(JSON, nullable=False, default=dict)

    # Convenience denormalized fields for fast dashboard queries
    last_node     = Column(String(100))          # e.g. "project", "interview"
    match_pct     = Column(Float)                # latest match_percentage
    skill_gaps    = Column(JSON, default=list)   # latest skill_gaps list
    completed_agents = Column(JSON, default=list)

    status        = Column(String(20), default="active")
    created_at    = Column(DateTime(timezone=True), default=_now)
    updated_at    = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    # Relationships
    user          = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<AgentSession {self.id} user={self.user_id} node={self.last_node}>"


# ── TPOReport (Batch Readiness Report) ────────────────────────────────────────

class TPOReport(Base):
    """
    Aggregated batch-wide skill gap report generated by the InstitutionalAnalyst node.
    Cached per org; regenerated on demand or on a schedule.
    """
    __tablename__ = "tpo_reports"

    id            = Column(String(36), primary_key=True, default=_uuid)
    org_id        = Column(String(36), ForeignKey("organizations.id",
                           ondelete="CASCADE"), nullable=False, index=True)

    # Full report payload (skill gaps, match distributions, readiness score)
    report_data   = Column(JSON, nullable=False, default=dict)

    # Quick-access summary fields
    total_students   = Column(Integer, default=0)
    avg_match_pct    = Column(Float)
    top_skill_gaps   = Column(JSON, default=list)   # [{"skill": "...", "count": N}]
    readiness_score  = Column(Float)                # 0-100 composite score

    generated_at  = Column(DateTime(timezone=True), default=_now)
    expires_at    = Column(DateTime(timezone=True))  # cache TTL

    # Relationships
    organization  = relationship("Organization", back_populates="tpo_reports")

    def __repr__(self) -> str:
        return f"<TPOReport org={self.org_id} score={self.readiness_score}>"


# ── AnalysisLog (Per-Run Audit Trail) ─────────────────────────────────────────

class AnalysisLog(Base):
    """
    Immutable audit record written after every successful AnalyzerAgent run.
    Powers the TPO analytics counter and historical reporting.
    """
    __tablename__ = "analysis_logs"

    id         = Column(String(36), primary_key=True, default=_uuid)
    org_id     = Column(String(36), ForeignKey("organizations.id",
                        ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("users.id",
                        ondelete="SET NULL"), nullable=True, index=True)

    model_used   = Column(String(120))          # e.g. "llama-3.3-70b-versatile"
    match_score  = Column(Float)                # match_percentage from AnalyzerAgent
    timestamp    = Column(DateTime(timezone=True), default=_now, nullable=False, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="analysis_logs")
    student      = relationship("User", foreign_keys=[student_id])

    def __repr__(self) -> str:
        return f"<AnalysisLog org={self.org_id} student={self.student_id} score={self.match_score}>"


# ── TPOLiveSession (Live Session Management) ──────────────────────────────────

class TPOLiveSession(Base):
    """
    Represents a live session opened by a TPO for their organisation.
    Students join using the session_code; the session tracks participation
    and analysis counts in real time.

    status: "active" | "ended"
    """
    __tablename__ = "tpo_live_sessions"

    id                  = Column(String(36), primary_key=True, default=_uuid)
    org_id              = Column(String(36), ForeignKey("organizations.id",
                                 ondelete="CASCADE"), nullable=False, index=True)
    created_by_user_id  = Column(String(36), ForeignKey("users.id",
                                 ondelete="SET NULL"), nullable=True, index=True)
    session_code        = Column(String(20), unique=True, nullable=False, index=True)
    status              = Column(String(10), default="active", nullable=False)
                          # "active" | "ended"
    started_at          = Column(DateTime(timezone=True), default=_now, nullable=False)
    ended_at            = Column(DateTime(timezone=True), nullable=True)
    participant_count   = Column(Integer, default=0, nullable=False)
    analyses_completed  = Column(Integer, default=0, nullable=False)

    # Relationships
    organization        = relationship("Organization")
    created_by          = relationship("User", foreign_keys=[created_by_user_id])
    participants        = relationship("SessionParticipant",
                                       back_populates="session",
                                       cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<TPOLiveSession {self.id} org={self.org_id} status={self.status}>"


# ── SessionParticipant (Session Membership) ───────────────────────────────────

class SessionParticipant(Base):
    """
    Records a student's participation in a TPOLiveSession.
    The unique constraint on (session_id, student_id) prevents duplicate entries.
    """
    __tablename__ = "session_participants"
    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="uq_session_participant"),
    )

    id                  = Column(String(36), primary_key=True, default=_uuid)
    session_id          = Column(String(36), ForeignKey("tpo_live_sessions.id",
                                 ondelete="CASCADE"), nullable=False, index=True)
    student_id          = Column(String(36), ForeignKey("users.id",
                                 ondelete="CASCADE"), nullable=False, index=True)
    joined_at           = Column(DateTime(timezone=True), default=_now, nullable=False)
    analyses_completed  = Column(Integer, default=0, nullable=False)

    # Relationships
    session             = relationship("TPOLiveSession", back_populates="participants")
    student             = relationship("User", foreign_keys=[student_id])

    def __repr__(self) -> str:
        return f"<SessionParticipant session={self.session_id} student={self.student_id}>"
