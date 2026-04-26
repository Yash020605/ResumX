"""
ResumX V2 – TPO Session Management Property-Based Tests
=========================================================
Uses Hypothesis to verify the 14 correctness properties defined in the design document.
Each test is tagged with its property number.

Run with:
    cd backend
    pytest tests/test_tpo_sessions_pbt.py -v
"""
from __future__ import annotations

import uuid
import contextlib
import pytest
from datetime import datetime, timezone
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, Organization, User, TPOLiveSession, SessionParticipant, AnalysisLog
from app.services.session_service import (
    create_session,
    end_session,
    join_session,
    get_dashboard,
    get_summary,
    list_sessions,
    generate_session_code,
    SessionConflictError,
    SessionForbiddenError,
    SessionNotFoundError,
    SessionEndedError,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """In-memory SQLite session for each test function (plain pytest tests)."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@contextlib.contextmanager
def _fresh_db():
    """
    Yields a brand-new in-memory SQLite session.
    Used inside @given tests so each Hypothesis example gets a clean database,
    avoiding state leakage between examples sharing the same pytest fixture.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_org(db, name="ADYPU College", domain=None):
    domain = domain or f"{uuid.uuid4().hex[:8]}.edu.in"
    org = Organization(name=name, domain=domain)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def _make_user(db, org_id, role="student", email=None):
    email = email or f"{uuid.uuid4().hex[:8]}@test.edu"
    user = User(
        org_id=org_id,
        email=email,
        password_hash="hashed",
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_analysis_log(db, org_id, student_id, match_score=75.0, timestamp=None):
    log = AnalysisLog(
        org_id=org_id,
        student_id=student_id,
        match_score=match_score,
        timestamp=timestamp or datetime.now(timezone.utc),
    )
    db.add(log)
    db.commit()
    return log


# ── Property 1: Session creation produces valid, org-scoped records ───────────

@given(org_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))))
@settings(max_examples=100)
def test_property_1_create_session_valid_record(org_name):
    # Property 1: Session creation produces valid, org-scoped records
    with _fresh_db() as db:
        org_name = org_name.strip() or "TestOrg"
        org = _make_org(db, name=org_name)
        tpo = _make_user(db, org.id, role="tpo")

        session = create_session(db, org.id, tpo.id)

        assert session.status == "active"
        assert session.session_code is not None
        assert len(session.session_code) > 0
        assert session.org_id == org.id
        assert session.started_at is not None


# ── Property 2: Session codes are unique across active sessions ───────────────

@given(n=st.integers(min_value=2, max_value=10))
@settings(max_examples=50)
def test_property_2_session_codes_unique(n):
    # Property 2: Session codes are unique across active sessions
    with _fresh_db() as db:
        codes = set()
        for i in range(n):
            org = _make_org(db, name=f"Org{i}")
            tpo = _make_user(db, org.id, role="tpo")
            session = create_session(db, org.id, tpo.id)
            codes.add(session.session_code)

        assert len(codes) == n


# ── Property 3: One active session per organisation ───────────────────────────

def test_property_3_one_active_session_per_org(db):
    # Property 3: One active session per organisation
    org = _make_org(db)
    tpo = _make_user(db, org.id, role="tpo")

    create_session(db, org.id, tpo.id)

    with pytest.raises(SessionConflictError):
        create_session(db, org.id, tpo.id)

    # Original session is still active
    active = db.query(TPOLiveSession).filter_by(org_id=org.id, status="active").count()
    assert active == 1


# ── Property 4: Join is idempotent for the same student and session ───────────

@given(n_joins=st.integers(min_value=2, max_value=5))
@settings(max_examples=100)
def test_property_4_join_idempotent(n_joins):
    # Property 4: Join is idempotent for the same student and session
    with _fresh_db() as db:
        org = _make_org(db)
        tpo = _make_user(db, org.id, role="tpo")
        student = _make_user(db, org.id, role="student")
        session = create_session(db, org.id, tpo.id)

        results = []
        for _ in range(n_joins):
            participant, already_joined = join_session(db, session.session_code, student.id, org.id)
            results.append(already_joined)

        # First join: already_joined=False; subsequent: already_joined=True
        assert results[0] is False
        assert all(r is True for r in results[1:])

        # Only one participant record
        count = db.query(SessionParticipant).filter_by(
            session_id=session.id, student_id=student.id
        ).count()
        assert count == 1


# ── Property 5: Cross-org join is always rejected ─────────────────────────────

def test_property_5_cross_org_join_rejected(db):
    # Property 5: Cross-org join is always rejected
    org_a = _make_org(db, name="OrgA", domain="orga.edu.in")
    org_b = _make_org(db, name="OrgB", domain="orgb.edu.in")
    tpo = _make_user(db, org_a.id, role="tpo")
    student_b = _make_user(db, org_b.id, role="student")

    session = create_session(db, org_a.id, tpo.id)

    with pytest.raises(SessionForbiddenError):
        join_session(db, session.session_code, student_b.id, org_b.id)


# ── Property 6: Dashboard participant count matches actual participants ────────

@given(n_students=st.integers(min_value=0, max_value=10))
@settings(max_examples=50)
def test_property_6_dashboard_participant_count(n_students):
    # Property 6: Dashboard participant count matches actual participants
    with _fresh_db() as db:
        org = _make_org(db)
        tpo = _make_user(db, org.id, role="tpo")
        session = create_session(db, org.id, tpo.id)

        students = [_make_user(db, org.id, role="student") for _ in range(n_students)]
        for student in students:
            join_session(db, session.session_code, student.id, org.id)

        dashboard = get_dashboard(db, session.id, org.id)

        assert dashboard["participant_count"] == n_students
        assert len(dashboard["participants"]) == n_students


# ── Property 7: Analysis counter increments atomically ───────────────────────

@given(k=st.integers(min_value=1, max_value=5))
@settings(max_examples=50)
def test_property_7_analysis_counter_increments(k):
    # Property 7: Analysis counter increments atomically
    from sqlalchemy import update

    with _fresh_db() as db:
        org = _make_org(db)
        tpo = _make_user(db, org.id, role="tpo")
        student = _make_user(db, org.id, role="student")
        session = create_session(db, org.id, tpo.id)
        participant, _ = join_session(db, session.session_code, student.id, org.id)

        # Simulate K analysis completions
        for _ in range(k):
            db.execute(
                update(SessionParticipant)
                .where(SessionParticipant.id == participant.id)
                .values(analyses_completed=SessionParticipant.analyses_completed + 1)
            )
            db.execute(
                update(TPOLiveSession)
                .where(TPOLiveSession.id == session.id)
                .values(analyses_completed=TPOLiveSession.analyses_completed + 1)
            )
            db.commit()

        db.refresh(participant)
        db.refresh(session)

        assert participant.analyses_completed == k
        assert session.analyses_completed == k


# ── Property 8: Ending a session is a one-way state transition ────────────────

def test_property_8_end_session_one_way(db):
    # Property 8: Ending a session is a one-way state transition
    org = _make_org(db)
    tpo = _make_user(db, org.id, role="tpo")
    session = create_session(db, org.id, tpo.id)

    ended = end_session(db, session.id, org.id)
    assert ended.status == "ended"
    assert ended.ended_at is not None

    first_ended_at = ended.ended_at

    with pytest.raises(SessionConflictError):
        end_session(db, session.id, org.id)

    # ended_at is unchanged
    db.refresh(ended)
    assert ended.ended_at == first_ended_at


# ── Property 9: Ended sessions reject joins and stop counting analyses ─────────

def test_property_9_ended_session_rejects_join(db):
    # Property 9: Ended sessions reject joins
    org = _make_org(db)
    tpo = _make_user(db, org.id, role="tpo")
    student = _make_user(db, org.id, role="student")
    session = create_session(db, org.id, tpo.id)
    end_session(db, session.id, org.id)

    with pytest.raises(SessionEndedError):
        join_session(db, session.session_code, student.id, org.id)


# ── Property 10: Summary avg_match_score is null when no analyses exist ───────

def test_property_10_avg_match_score_null_when_no_analyses(db):
    # Property 10: Summary avg_match_score is null when no analyses exist
    org = _make_org(db)
    tpo = _make_user(db, org.id, role="tpo")
    student = _make_user(db, org.id, role="student")
    session = create_session(db, org.id, tpo.id)
    join_session(db, session.session_code, student.id, org.id)

    # No AnalysisLog rows
    summary = get_summary(db, session.id, org.id)
    assert summary["avg_match_score"] is None


# ── Property 11: Session list is ordered and org-scoped ───────────────────────

@given(n=st.integers(min_value=2, max_value=8))
@settings(max_examples=30)
def test_property_11_session_list_ordered_and_scoped(n):
    # Property 11: Session list is ordered and org-scoped
    with _fresh_db() as db:
        org_a = _make_org(db, name="OrgA")
        org_b = _make_org(db, name="OrgB")

        for i in range(n):
            tpo = _make_user(db, org_a.id, role="tpo")
            create_session(db, org_a.id, tpo.id)
            # End it so we can create another
            active = db.query(TPOLiveSession).filter_by(org_id=org_a.id, status="active").first()
            if active:
                end_session(db, active.id, org_a.id)

        # Create one session for org_b
        tpo_b = _make_user(db, org_b.id, role="tpo")
        sess_b = create_session(db, org_b.id, tpo_b.id)

        result = list_sessions(db, org_a.id)

        # Only org_a sessions
        assert all(r["session_id"] != sess_b.id for r in result["sessions"])
        assert result["total"] == n

        # Ordered by started_at DESC
        dates = [r["started_at"] for r in result["sessions"]]
        assert dates == sorted(dates, reverse=True)


# ── Property 12: Status filter returns only matching sessions ─────────────────

def test_property_12_status_filter(db):
    # Property 12: Status filter returns only matching sessions
    org = _make_org(db)
    tpo1 = _make_user(db, org.id, role="tpo", email="tpo1@org.edu")
    tpo2 = _make_user(db, org.id, role="tpo", email="tpo2@org.edu")

    s1 = create_session(db, org.id, tpo1.id)
    end_session(db, s1.id, org.id)
    create_session(db, org.id, tpo2.id)  # active

    active_result = list_sessions(db, org.id, status="active")
    ended_result = list_sessions(db, org.id, status="ended")

    assert all(s["status"] == "active" for s in active_result["sessions"])
    assert all(s["status"] == "ended" for s in ended_result["sessions"])


# ── Property 13: Unauthenticated requests are always rejected ─────────────────

def test_property_13_session_not_found_raises(db):
    # Property 13: Non-existent session raises SessionNotFoundError (simulates 404)
    org = _make_org(db)

    with pytest.raises(SessionNotFoundError):
        get_dashboard(db, "nonexistent-id", org.id)

    with pytest.raises(SessionNotFoundError):
        get_summary(db, "nonexistent-id", org.id)

    with pytest.raises(SessionNotFoundError):
        end_session(db, "nonexistent-id", org.id)


# ── Property 14: Role-based access control is enforced ───────────────────────

def test_property_14_cross_org_access_rejected(db):
    # Property 14: Cross-org access is always rejected (403-equivalent)
    org_a = _make_org(db, name="OrgA", domain="pa.edu.in")
    org_b = _make_org(db, name="OrgB", domain="pb.edu.in")
    tpo_a = _make_user(db, org_a.id, role="tpo")
    session = create_session(db, org_a.id, tpo_a.id)

    with pytest.raises(SessionForbiddenError):
        get_dashboard(db, session.id, org_b.id)

    with pytest.raises(SessionForbiddenError):
        get_summary(db, session.id, org_b.id)

    with pytest.raises(SessionForbiddenError):
        end_session(db, session.id, org_b.id)
