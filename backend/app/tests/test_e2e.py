"""
End-to-End User Journey Test
Simulates the complete user lifecycle:
1. User Signup (with mandatory age and sanitized input)
2. User Login (credentials verification)
3. 2FA Verification via Master Demo Bypass (123456)
4. Dashboard Load (fetching stats, timeline, memories using JWT Bearer token)
5. Validates session state updates and token integrity
"""

import sys
import os
import uuid
import pytest
from fastapi.testclient import TestClient

# Ensure backend package is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app
from app.database.firestore_client import db_client


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_full_user_journey_e2e(client):
    """
    Executes full E2E journey:
    Signup -> Login -> 2FA Bypass (123456) -> Dashboard & Timeline Loading
    """
    unique_suffix = uuid.uuid4().hex[:6]
    test_email = f"e2e_keeper_{unique_suffix}@heritage.vault"
    test_phone = "+919876543210"
    test_password = "E2E_SecurePassword!2026"
    test_name = "Grandmother Lakshmi"
    test_age = 76

    # =========================================================================
    # STEP 1: USER SIGNUP
    # =========================================================================
    signup_payload = {
        "full_name": test_name,
        "age": test_age,
        "email": test_email,
        "phone": test_phone,
        "password": test_password
    }
    signup_resp = client.post("/api/auth/signup", json=signup_payload)
    assert signup_resp.status_code == 201, f"Signup failed: {signup_resp.text}"
    signup_data = signup_resp.json()
    user_id = signup_data["user_id"]
    assert user_id.startswith("user_")
    assert signup_data["requires_otp"] is True
    assert signup_data["user_data"]["age"] == test_age

    # =========================================================================
    # STEP 2: USER LOGIN (TRIGGERS 2FA OTP)
    # =========================================================================
    login_payload = {
        "email": test_email,
        "password": test_password
    }
    login_resp = client.post("/api/auth/login", json=login_payload)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    assert login_data["user_id"] == user_id
    assert login_data["requires_otp"] is True

    # =========================================================================
    # STEP 3: OTP VERIFICATION VIA MASTER BYPASS (123456)
    # =========================================================================
    verify_payload = {
        "user_id": user_id,
        "otp_code": "123456"
    }
    verify_resp = client.post("/api/auth/verify-otp", json=verify_payload)
    assert verify_resp.status_code == 200, f"OTP verification failed: {verify_resp.text}"
    verify_data = verify_resp.json()
    assert "access_token" in verify_data
    assert verify_data["user_data"]["email"] == test_email
    assert verify_data["user_data"]["name"] == test_name
    access_token = verify_data["access_token"]
    assert len(access_token) > 20

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # =========================================================================
    # STEP 4: DASHBOARD LOAD (STATS, MEMORIES, TIMELINE)
    # =========================================================================
    # 4a. Health Score & Vault Stats
    stats_resp = client.get("/api/memories/stats/health-score", headers=auth_headers)
    assert stats_resp.status_code == 200, f"Stats load failed: {stats_resp.text}"
    stats_data = stats_resp.json()
    assert "completion_percentage" in stats_data
    assert "total_memories" in stats_data

    # 4b. Timeline & Eras
    eras_resp = client.get("/api/timeline/eras", headers=auth_headers)
    assert eras_resp.status_code == 200, f"Eras load failed: {eras_resp.text}"
    eras_data = eras_resp.json()
    assert "eras" in eras_data

    timeline_resp = client.get("/api/timeline/", headers=auth_headers)
    assert timeline_resp.status_code == 200, f"Timeline load failed: {timeline_resp.text}"
    timeline_data = timeline_resp.json()
    assert isinstance(timeline_data, list)

    # 4c. Paginated Memories (Default limit 20, offset 0)
    memories_resp = client.get("/api/memories/?limit=20&offset=0", headers=auth_headers)
    assert memories_resp.status_code == 200, f"Memories load failed: {memories_resp.text}"
    memories_data = memories_resp.json()
    assert isinstance(memories_data, list)

    # 4d. Map Points & Migrations
    map_resp = client.get("/api/map/points", headers=auth_headers)
    assert map_resp.status_code == 200, f"Map points load failed: {map_resp.text}"
    map_data = map_resp.json()
    assert isinstance(map_data, list)

    mig_resp = client.get("/api/map/migrations", headers=auth_headers)
    assert mig_resp.status_code == 200
    assert "paths" in mig_resp.json()

    # Filtered memories & timeline sort
    filtered_mem = client.get("/api/memories/?era=1960s&limit=5&offset=0", headers=auth_headers)
    assert filtered_mem.status_code == 200

    timeline_desc = client.get("/api/timeline/?sort=desc", headers=auth_headers)
    assert timeline_desc.status_code == 200

    # Grounded Q&A
    ask_resp = client.post("/api/ask/", json={"question": "What temples were visited in childhood?"}, headers=auth_headers)
    assert ask_resp.status_code == 200
    assert "answer" in ask_resp.json()

    # 4e. Create, Read, Delete Memory
    create_mem_resp = client.post(
        "/api/memories/",
        json={
            "title": "Summer Vacations in Tanjore",
            "raw_text": "We plucked raw mangoes with salt and chili powder every afternoon."
        },
        headers=auth_headers
    )
    assert create_mem_resp.status_code == 200
    mem_id = create_mem_resp.json().get("id")
    assert mem_id is not None

    get_mem_resp = client.get(f"/api/memories/{mem_id}", headers=auth_headers)
    assert get_mem_resp.status_code == 200
    assert get_mem_resp.json().get("id") == mem_id

    del_mem_resp = client.delete(f"/api/memories/{mem_id}", headers=auth_headers)
    assert del_mem_resp.status_code == 200

    # Emotion Timeline & Graph Connections
    emo_resp = client.get("/api/memories/stats/emotion-timeline", headers=auth_headers)
    assert emo_resp.status_code == 200

    conn_resp = client.get("/api/memories/stats/connections", headers=auth_headers)
    assert conn_resp.status_code == 200

    # Custodian Designation & Retrieval
    cust_post = client.post(
        "/api/memories/legacy/custodian",
        json={
            "custodian_name": "Ravi Iyer",
            "custodian_email": "ravi@heritage.org",
            "relationship": "Grandson"
        },
        headers=auth_headers
    )
    assert cust_post.status_code == 200

    cust_get = client.get("/api/memories/legacy/custodian", headers=auth_headers)
    assert cust_get.status_code == 200

    # 4f. System Health & Auth Lifecycle
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json().get("status") == "healthy"

    resend_resp = client.post("/api/auth/resend-otp", json={"user_id": user_id})
    assert resend_resp.status_code == 200

    logout_resp = client.post("/api/auth/logout", headers=auth_headers)
    assert logout_resp.status_code == 200

    # Journey succeeded completely
    print("\n✅ E2E Full User Journey Succeeded: Signup -> Login -> OTP Bypass (123456) -> Dashboard & Full Memory Lifecycle.")


def test_explicit_otp_master_bypass_session_verification(client):
    """
    Explicitly tests the master OTP bypass (123456):
    1. Rejects invalid OTP
    2. Accepts master bypass '123456'
    3. Verifies session access_token and user profile are properly set
    4. Authenticates protected API requests with Bearer token
    """
    suffix = uuid.uuid4().hex[:6]
    email = f"bypass_user_{suffix}@heritage.vault"
    signup_resp = client.post("/api/auth/signup", json={
        "full_name": "Bypass Test Elder",
        "age": 80,
        "email": email,
        "phone": "+919876543210",
        "password": "Password123!"
    })
    assert signup_resp.status_code == 201
    user_id = signup_resp.json()["user_id"]

    # 1. Login user to initiate 2FA
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    assert login_resp.status_code == 200
    assert login_resp.json()["requires_otp"] is True

    # 2. Reject incorrect OTP
    bad_verify = client.post("/api/auth/verify-otp", json={"user_id": user_id, "otp_code": "000000"})
    assert bad_verify.status_code == 400

    # 3. Master bypass 123456 verification
    good_verify = client.post("/api/auth/verify-otp", json={"user_id": user_id, "otp_code": "123456"})
    assert good_verify.status_code == 200
    data = good_verify.json()

    # 4. Verify session state fields
    assert "access_token" in data
    token = data["access_token"]
    assert len(token) > 20
    assert "user_data" in data
    assert data["user_data"]["email"] == email

    # 5. Verify protected endpoint accepts the session token
    auth_header = {"Authorization": f"Bearer {token}"}
    protected_resp = client.get("/api/memories/stats/health-score", headers=auth_header)
    assert protected_resp.status_code == 200
    assert "completion_percentage" in protected_resp.json()

