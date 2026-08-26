"""
AI Interviewer Router
Dedicated endpoints for the Relentless AI Interviewer workflow:
- POST /api/interview/start
- POST /api/interview/respond
- POST /api/interview/finish
- GET /api/interview/{session_id}
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from ..models.memory import (
    StartInterviewRequest,
    InterviewResponseRequest,
    FinishInterviewRequest,
    InterviewSession
)
from ..middleware.permissions import get_current_user_id, sanitize_input_text
from ..services.interview_service import interview_service, FALLBACK_QUESTIONS
from ..database.firestore_client import db_client

router = APIRouter(prefix="/api/interview", tags=["Relentless AI Interviewer"])


@router.post("/start", response_model=InterviewSession)
async def start_interview_session(
    req: StartInterviewRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Phase 1: Initializes an interview session, asks the initial 3 follow-up questions
    grounded in sensory details, people, places, emotions, and time.
    """
    req.initial_thought = sanitize_input_text(req.initial_thought or "")
    session = await interview_service.start_interview(user_id=user_id, request=req)
    return session


@router.post("/respond")
async def submit_interview_response(
    req: InterviewResponseRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Phase 2 & 3: Records the elder's spoken or typed answer and queries Gemini
    with the hardcoded system prompt to generate the NEXT 3 follow-up questions.
    """
    req.user_response = sanitize_input_text(req.user_response)
    if not req.user_response:
        raise HTTPException(status_code=400, detail="Response text cannot be empty.")

    try:
        session, should_finish = await interview_service.respond_to_interview(
            user_id=user_id,
            request=req
        )
        return {
            "session_id": session.session_id,
            "turn": session.current_turn,
            "is_completed": session.is_completed,
            "should_finish": should_finish,
            "next_questions": session.current_questions,
            "total_exchanges": len(session.exchanges)
        }
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))


@router.post("/finish")
async def finish_interview_session(
    req: FinishInterviewRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Phase 4 & 5: Aggregates the entire transcript into a cohesive, first-person
    narrative story using Gemini 1.5 Flash and triggers the standard memory processor.
    """
    if req.custom_title:
        req.custom_title = sanitize_input_text(req.custom_title)

    try:
        result = await interview_service.finish_interview(
            user_id=user_id,
            request=req
        )
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))


@router.get("/{session_id}", response_model=InterviewSession)
async def get_interview_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Retrieves session transcript and current status."""
    data = await db_client.get_interview_session(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    if data.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this session.")
    return data
