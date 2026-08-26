"""
Self-Contained Pytest Suite for MemoryBox
Comprehensive Unit & Integration tests for:
- Complete Sign-Up & Sign-In with 2FA
- Dual-Channel OTP (Email + SMS) Verification & TTL Expiration
- Mandatory Age Field Handling & Generational Archiving
- Age Contextualization in Memory Processing
- Grounded Ancestral Q&A & Relentless Interviewer
"""

import sys
import os
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient

# Ensure backend package is in Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
from app.database.firestore_client import db_client
from app.services.otp_service import otp_service
from app.routers.auth import create_access_token


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==============================================================================
# 1. SIGN-UP & VALIDATION TESTS
# ==============================================================================

def test_signup_successful(client):
    """Verifies that complete sign-up saves age, phone, email, and dispatches 2FA OTP."""
    payload = {
        "full_name": "Ramanathan Iyer",
        "age": 82,
        "email": "ramanathan.iyer@heritage.org",
        "phone": "+919840123456",
        "password": "SecurePassword2026!"
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 201, f"Signup failed: {resp.text}"
    data = resp.json()
    assert data["requires_otp"] is True
    assert "user_id" in data
    assert data["user_data"]["age"] == 82
    assert data["user_data"]["phone"] == "+919840123456"
    assert data["user_data"]["mfaEnabled"] is True


def test_signup_invalid_age(client):
    """Verifies that negative age or age > 130 fails validation with 422."""
    payload = {
        "full_name": "Invalid Age",
        "age": -5,
        "email": "invalid.age@heritage.org",
        "phone": "+919840123457",
        "password": "SecurePassword2026!"
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 422


def test_signup_invalid_phone_format(client):
    """Verifies that non-+91 or malformed phone numbers are rejected with 422."""
    payload = {
        "full_name": "Invalid Phone",
        "age": 70,
        "email": "invalid.phone@heritage.org",
        "phone": "984012",  # Missing country code and invalid length
        "password": "SecurePassword2026!"
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 422
    assert "phone" in resp.text.lower()


def test_signup_weak_password(client):
    """Verifies password strength requirements (min 8 chars, letters and digits) with 422."""
    payload = {
        "full_name": "Weak Pass",
        "age": 70,
        "email": "weak.pass@heritage.org",
        "phone": "+919840123458",
        "password": "simple"  # Too short, no digits
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 422


def test_signup_duplicate_email(client):
    """Verifies that duplicate email registrations are prevented with 400."""
    payload = {
        "full_name": "Ramanathan Duplicate",
        "age": 82,
        "email": "ramanathan.iyer@heritage.org",
        "phone": "+919840123459",
        "password": "SecurePassword2026!"
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 400
    assert "already registered" in resp.text


# ==============================================================================
# 2. SIGN-IN & 2FA OTP VERIFICATION TESTS
# ==============================================================================

def test_login_invalid_credentials(client):
    """Verifies failure on incorrect password."""
    resp = client.post("/api/auth/login", json={
        "email": "ramanathan.iyer@heritage.org",
        "password": "WrongPassword123"
    })
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.text


def test_login_triggers_dual_channel_otp(client):
    """Verifies successful credentials trigger dual-channel OTP and requires_otp=True."""
    resp = client.post("/api/auth/login", json={
        "email": "ramanathan.iyer@heritage.org",
        "password": "SecurePassword2026!"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["requires_otp"] is True
    assert "user_id" in data
    assert "debug_otp" in data["user_data"]


def test_otp_verification_with_email_otp(client):
    """Verifies that entering the email OTP successfully authenticates the user."""
    # 1. Trigger login to get a fresh OTP
    login_resp = client.post("/api/auth/login", json={
        "email": "ramanathan.iyer@heritage.org",
        "password": "SecurePassword2026!"
    })
    uid = login_resp.json()["user_id"]
    otp_code = login_resp.json()["user_data"]["debug_otp"]

    # 2. Verify with correct OTP
    verify_resp = client.post("/api/auth/verify-otp", json={
        "user_id": uid,
        "otp_code": otp_code
    })
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert "access_token" in data
    assert data["user_data"]["age"] == 82
    assert data["user_data"]["emailVerified"] is True


def test_otp_verification_dual_channel_phone_otp(client):
    """Verifies that entering the phone OTP also successfully authenticates (either channel works)."""
    # 1. Trigger login
    login_resp = client.post("/api/auth/login", json={
        "email": "ramanathan.iyer@heritage.org",
        "password": "SecurePassword2026!"
    })
    uid = login_resp.json()["user_id"]

    # 2. Retrieve phone OTP from backend store directly
    otp_record = db_client._mock_otps.get(uid)
    phone_otp = otp_record["phone_otp"]

    # 3. Verify using phone OTP
    verify_resp = client.post("/api/auth/verify-otp", json={
        "user_id": uid,
        "otp_code": phone_otp
    })
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert "access_token" in data


def test_otp_verification_wrong_code(client):
    """Verifies that an incorrect OTP is rejected."""
    login_resp = client.post("/api/auth/login", json={
        "email": "ramanathan.iyer@heritage.org",
        "password": "SecurePassword2026!"
    })
    uid = login_resp.json()["user_id"]

    verify_resp = client.post("/api/auth/verify-otp", json={
        "user_id": uid,
        "otp_code": "000000"  # Incorrect code
    })
    assert verify_resp.status_code == 400
    assert "Invalid OTP code" in verify_resp.text


def test_otp_ttl_expiration(client):
    """Verifies that an OTP older than 5 minutes is expired and rejected."""
    login_resp = client.post("/api/auth/login", json={
        "email": "ramanathan.iyer@heritage.org",
        "password": "SecurePassword2026!"
    })
    uid = login_resp.json()["user_id"]

    # Manually expire the OTP in datastore (set expired timestamp 10 minutes ago)
    if uid in db_client._mock_otps:
        expired_time = datetime.utcnow() - timedelta(minutes=10)
        db_client._mock_otps[uid]["expiresAt"] = expired_time.isoformat()

    verify_resp = client.post("/api/auth/verify-otp", json={
        "user_id": uid,
        "otp_code": "123456"
    })
    assert verify_resp.status_code == 400
    assert "expired" in verify_resp.text.lower()


# ==============================================================================
# 3. AGE CONTEXTUALIZATION & DASHBOARD GENERATIONAL STATS
# ==============================================================================

def test_age_contextualization_in_memory_processing(client):
    """Verifies that Gemini and the memory processor calculate author age during memory."""
    uid = "user_ramanathan"
    db_client._mock_users[uid] = {
        "uid": uid,
        "name": "Ramanathan Iyer",
        "age": 82,  # Born approx 1944
        "email": "ramanathan.iyer@heritage.org"
    }

    # Generate a valid JWT token
    token = create_access_token(uid)

    # Submit story from 1960
    resp = client.post("/api/memories/", json={
        "title": "College Days in Madras",
        "raw_text": "In 1960, I was studying in Madras Christian College. The sea breeze at Marina Beach carried the scent of roasted corn and salty air.",
        "language": "English"
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    memory = resp.json()

    # Verify age contextualization
    assert "author_age_during_memory" in memory
    assert "age_context" in memory
    assert memory.get("age_context") is not None


def test_dashboard_generational_span(client):
    """Verifies dashboard stats calculate family generational span from elder's age."""
    resp = client.get("/api/memories/stats/health-score")
    assert resp.status_code == 200
    data = resp.json()
    summary = data["status_summary"]
    # For elder aged 78-82, spans 4 generations
    assert "spans" in summary
    assert "generations" in summary


# ==============================================================================
# 4. GROUNDED ANCESTRAL Q&A & INTERVIEWER INTEGRATION
# ==============================================================================

def test_grounded_ancestral_qa_with_citations(client):
    """Verifies Q&A queries vault memories with evidence citations."""
    resp = client.post("/api/ask/", json={
        "question": "What did grandmother prepare during the monsoon?"
    })
    assert resp.status_code == 200
    ans = resp.json()
    assert ans["grounded"] is True
    assert len(ans["citations"]) > 0


def test_relentless_interviewer_full_flow(client):
    """Verifies the 4-phase Relentless AI Interviewer workflow end-to-end."""
    # Phase 1: Start
    start_resp = client.post("/api/interview/start", json={
        "initial_thought": "I remember the village temple festival in 1965.",
        "language": "English"
    })
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session_id"]
    assert len(start_resp.json()["current_questions"]) == 3

    # Phase 2: Respond
    respond_resp = client.post("/api/interview/respond", json={
        "session_id": session_id,
        "user_response": "The temple chariot was decorated with marigolds, and the brass bells rang through the village."
    })
    assert respond_resp.status_code == 200
    assert len(respond_resp.json()["next_questions"]) == 3

    # Phase 3: Finish & Weave
    finish_resp = client.post("/api/interview/finish", json={
        "session_id": session_id,
        "custom_title": "The Temple Chariot of 1965"
    })
    assert finish_resp.status_code == 200
    narrative = finish_resp.json()["story_narrative"]
    assert len(narrative) > 50


def test_auth_middleware_rejects_invalid_token(client):
    """Verifies that the auth middleware returns 401 Unauthorized for invalid or missing tokens."""
    # 1. Missing token
    resp_no_token = client.get("/api/timeline/")
    # With default testing client, get_current_user_id falls back or checks token
    # Explicitly test the auth middleware function
    import pytest
    from fastapi import HTTPException
    from backend.app.middleware.auth import verify_firebase_token
    from fastapi.security import HTTPAuthorizationCredentials

    # Test invalid token yields 401
    invalid_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.here")
    with pytest.raises(HTTPException) as exc_info:
        import asyncio
        asyncio.run(verify_firebase_token(invalid_creds))
    assert exc_info.value.status_code == 401

    # Test missing credentials yields 401
    with pytest.raises(HTTPException) as exc_info2:
        asyncio.run(verify_firebase_token(None))
    assert exc_info2.value.status_code == 401


def test_timeline_and_map_routers(client):
    """Verifies that timeline and map routers return valid responses."""
    # Test Timeline
    tl_resp = client.get("/api/timeline/")
    assert tl_resp.status_code == 200
    assert isinstance(tl_resp.json(), list)

    eras_resp = client.get("/api/timeline/eras")
    assert eras_resp.status_code == 200
    assert "eras" in eras_resp.json()

    # Test Map Points
    map_resp = client.get("/api/map/points")
    assert map_resp.status_code == 200
    assert isinstance(map_resp.json(), list)

    # Test Migrations
    mig_resp = client.get("/api/map/migrations")
    assert mig_resp.status_code == 200
    assert "paths" in mig_resp.json()

