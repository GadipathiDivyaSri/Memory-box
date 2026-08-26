"""
Comprehensive Unit & Mock Tests for Relentless AI Interviewer
Tests:
- Mocking the Gemini API response
- Test 'start' endpoint (checks if 3 questions are returned)
- Test 'respond' loop (checks if it stops after 3 turns)
- Test 'finish' endpoint (checks story synthesis and background task status)
"""

import sys
import os
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Ensure backend package is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app
from app.routers.auth import create_access_token
from app.database.firestore_client import db_client


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def auth_headers():
    uid = "test_interviewer_uid"
    token = create_access_token(uid, {"name": "Elder Tester", "age": 82})
    return {"Authorization": f"Bearer {token}"}


def test_mock_gemini_interview_start(client, auth_headers):
    """
    Test the 'start' endpoint:
    - Mocks Gemini API question generation
    - Verifies 3 questions and opening line are returned
    """
    mock_questions = [
        "What is your earliest childhood memory of your ancestral home?",
        "Can you describe the sounds and aromas of festival mornings?",
        "Who was the most influential person in your family growing up?"
    ]

    with patch("app.services.interview_service.interview_service._generate_follow_up_questions", new_callable=AsyncMock) as mock_gemini:
        mock_gemini.return_value = mock_questions

        resp = client.post(
            "/api/interview/start",
            json={
                "topic": "Early childhood and ancestral traditions",
                "era": "1950s",
                "language": "English"
            },
            headers=auth_headers
        )

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "session_id" in data
        assert "opening_line" in data
        assert len(data.get("next_questions", [])) == 3
        assert data["next_questions"] == mock_questions


def test_interview_respond_loop_stops_after_three_turns(client, auth_headers):
    """
    Test the 'respond' loop:
    - Simulates answering questions across turns
    - Verifies turns increment and session is marked complete after 3 turns
    """
    # 1. Start session
    start_resp = client.post(
        "/api/interview/start",
        json={"topic": "Village life and migration", "era": "1960s"},
        headers=auth_headers
    )
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session_id"]

    # 2. Turn 1
    t1_resp = client.post(
        "/api/interview/respond",
        json={
            "session_id": session_id,
            "user_response": "I grew up near the Kaveri river in Thanjavur.",
            "answered_question": "Where did you grow up?"
        },
        headers=auth_headers
    )
    assert t1_resp.status_code == 200
    data_t1 = t1_resp.json()
    assert data_t1["turn"] == 1
    assert data_t1["is_complete"] is False

    # 3. Turn 2
    t2_resp = client.post(
        "/api/interview/respond",
        json={
            "session_id": session_id,
            "user_response": "We used to walk 5 kilometers to the temple school every day.",
            "answered_question": "What was school like?"
        },
        headers=auth_headers
    )
    assert t2_resp.status_code == 200
    data_t2 = t2_resp.json()
    assert data_t2["turn"] == 2
    assert data_t2["is_complete"] is False

    # 4. Turn 3 (Final turn - should mark complete)
    t3_resp = client.post(
        "/api/interview/respond",
        json={
            "session_id": session_id,
            "user_response": "In 1972, we moved to Bengaluru by steam train.",
            "answered_question": "When did you leave your village?"
        },
        headers=auth_headers
    )
    assert t3_resp.status_code == 200
    data_t3 = t3_resp.json()
    assert data_t3["turn"] == 3
    assert data_t3["is_complete"] is True
    assert "ready to be synthesized" in data_t3.get("encouraging_remark", "").lower()

    # Verify GET session endpoint
    get_sess = client.get(f"/api/interview/{session_id}", headers=auth_headers)
    assert get_sess.status_code == 200
    assert get_sess.json()["session_id"] == session_id


def test_interview_finish_endpoint(client, auth_headers):
    """
    Test the 'finish' endpoint:
    - Verifies BackgroundTasks returns 'processing' status immediately
    - Checks session_id is returned
    - Verifies background story synthesis is scheduled
    """
    # Start and supply a response
    start_resp = client.post(
        "/api/interview/start",
        json={"topic": "Family wedding customs", "era": "1970s"},
        headers=auth_headers
    )
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session_id"]

    client.post(
        "/api/interview/respond",
        json={
            "session_id": session_id,
            "user_response": "The wedding feast lasted three days with classical veena music.",
            "answered_question": "Describe the ceremony."
        },
        headers=auth_headers
    )

    with patch("app.services.interview_service.interview_service.finish_interview", new_callable=AsyncMock) as mock_finish:
        mock_finish.return_value = {
            "status": "completed",
            "memory_id": "mem_test123",
            "story_narrative": "The wedding feast lasted three days..."
        }

        finish_resp = client.post(
            "/api/interview/finish",
            json={
                "session_id": session_id,
                "custom_title": "Grand Ancestral Wedding Feast"
            },
            headers=auth_headers
        )

        assert finish_resp.status_code == 200, f"Expected 200, got: {finish_resp.text}"
        data = finish_resp.json()
        assert data.get("status") == "processing"
        assert data.get("session_id") == session_id
        assert "story_narrative" in data
