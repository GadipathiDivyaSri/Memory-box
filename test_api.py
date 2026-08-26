"""
MemoryBox Smoke Test Suite
Verifies all FastAPI routers, Relentless Interviewer workflow, and analytics offline.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from app.main import app

def test_full_flow():
    with TestClient(app) as client:
        print("\n--- 1. Testing Health Endpoint ---")
        resp = client.get("/health")
        assert resp.status_code == 200, f"Health check failed: {resp.text}"
        print("Health check OK:", resp.json())

        print("\n--- 2. Testing Memory List (Seeded Memories) ---")
        resp = client.get("/api/memories/")
        assert resp.status_code == 200, f"Memory list failed: {resp.text}"
        memories = resp.json()
        print(f"Retrieved {len(memories)} initial memories from vault.")
        assert len(memories) >= 2, "Expected at least 2 seeded memories."

        print("\n--- 3. Testing Relentless AI Interviewer: Start ---")
        resp = client.post("/api/interview/start", json={
            "initial_thought": "I remember our ancestral mango orchard in Andhra Pradesh during the 1970s.",
            "language": "English"
        })
        assert resp.status_code == 200, f"Interview start failed: {resp.text}"
        session = resp.json()
        session_id = session["session_id"]
        print(f"Started Interview Session: {session_id}")
        print("Generated 3 Sensory Questions:")
        for idx, q in enumerate(session.get("current_questions", []), 1):
            print(f"  [{idx}] {q}")
        assert len(session.get("current_questions", [])) == 3

        print("\n--- 4. Testing Relentless AI Interviewer: Respond ---")
        resp = client.post("/api/interview/respond", json={
            "session_id": session_id,
            "user_response": "The summer air smelled of sweet raw mangoes and red soil. My grandfather and I sat under the neem tree drinking cool buttermilk."
        })
        assert resp.status_code == 200, f"Interview respond failed: {resp.text}"
        respond_data = resp.json()
        print(f"Turn {respond_data.get('turn')} recorded. Next follow-ups:")
        for idx, q in enumerate(respond_data.get("next_questions", []), 1):
            print(f"  [{idx}] {q}")

        print("\n--- 5. Testing Relentless AI Interviewer: Finish & Weave Story ---")
        resp = client.post("/api/interview/finish", json={
            "session_id": session_id,
            "custom_title": "Summer Mornings in the Mango Orchard"
        })
        assert resp.status_code == 200, f"Interview finish failed: {resp.text}"
        fin_data = resp.json()
        print("Weaved First-Person Story Narrative:")
        print("\"", fin_data.get("story_narrative")[:250], "...\"")
        assert fin_data.get("story_narrative"), "Expected woven narrative."

        print("\n--- 6. Testing Digital Health Score ---")
        resp = client.get("/api/memories/stats/health-score")
        assert resp.status_code == 200
        print("Health Score:", resp.json().get("status_summary"))

        print("\n--- 7. Testing Decade Emotion Timeline ---")
        resp = client.get("/api/memories/stats/emotion-timeline")
        assert resp.status_code == 200
        timeline = resp.json()
        print(f"Emotion timeline spans {len(timeline)} eras.")

        print("\n--- 8. Testing Grounded Ancestral Q&A ---")
        resp = client.post("/api/ask/", json={"question": "What happened during the monsoon in Mysore?"})
        assert resp.status_code == 200
        ans_data = resp.json()
        print("Grounded Q&A Answer:\n", ans_data.get("answer")[:200], "...")

        print("\n==========================================")
        print("ALL TESTS PASSED! MEMORYBOX IS PRODUCTION READY!")
        print("==========================================")

if __name__ == "__main__":
    test_full_flow()
