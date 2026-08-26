"""
Grounded Ancestral Q&A Router
Answers user and family questions strictly grounded in the preserved memories.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from ..models.memory import AskQuestionRequest, AskQuestionResponse
from ..middleware.permissions import get_current_user_id, sanitize_input_text
from ..services.gemini_service import gemini_service
from ..database.firestore_client import db_client

router = APIRouter(prefix="/api/ask", tags=["Grounded Ancestral Q&A"])


@router.post("/", response_model=AskQuestionResponse)
async def ask_ancestral_vault(
    req: AskQuestionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Submits a conversational question to the Family Heritage Vault.
    Gemini 1.5 Flash reasons strictly over the user's recorded memories
    and provides grounded answers with explicit story citations.
    """
    clean_question = sanitize_input_text(req.question)
    if len(clean_question) < 3:
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters long.")

    # Retrieve relevant memories for grounding
    vault_memories = await db_client.list_memories(
        user_id=user_id,
        era=req.era_filter,
        limit=20
    )

    result = await gemini_service.answer_grounded_question(
        question=clean_question,
        vault_memories=vault_memories
    )

    await db_client.log_audit_event(
        user_id=user_id,
        action="vault.queried",
        resource_id="grounded_qa",
        metadata={"question": clean_question, "grounded": result.get("grounded", False)}
    )

    return AskQuestionResponse(
        answer=result.get("answer", "No response generated."),
        grounded=result.get("grounded", False),
        citations=result.get("citations", []),
        related_people=result.get("related_people", []),
        related_places=result.get("related_places", [])
    )
