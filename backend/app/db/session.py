"""
ResumX V2 – SQLAlchemy Session Factory
=======================================
Provides a scoped session and Alembic-compatible engine.

DATABASE_URL priority:
  1. DATABASE_URL env var (Postgres in production)
  2. SQLite fallback  → resumx_local.db  (local dev, no Postgres needed)
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session

from app.db.models import Base

_POSTGRES_URL = os.getenv("DATABASE_URL", "")
_SQLITE_URL   = "sqlite:///resumx_local.db"


def _make_engine(url: str):
    if url.startswith("sqlite"):
        # SQLite: no pool_size / max_overflow, needs check_same_thread=False
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
        )
    return create_engine(
        url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False,
    )


def _resolve_engine():
    """Try Postgres first; fall back to SQLite automatically."""
    if _POSTGRES_URL:
        try:
            eng = _make_engine(_POSTGRES_URL)
            with eng.connect() as c:
                c.execute(text("SELECT 1"))
            print("[DB] Connected to Postgres.")
            return eng
        except Exception as exc:
            print(f"[DB] Postgres unavailable ({exc}). Falling back to SQLite.")

    print(f"[DB] Using SQLite → {_SQLITE_URL}")
    return _make_engine(_SQLITE_URL)


engine = _resolve_engine()

_SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
SessionLocal    = scoped_session(_SessionFactory)


def init_db() -> None:
    """Create all tables (idempotent). Use Alembic for migrations in production."""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
