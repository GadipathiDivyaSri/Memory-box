"""
Memories & Heritage Analytics Router
Endpoints for managing preserved stories, emotion trajectories, memory links,
digital health scores, and custodian legacy handover.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..models.memory import (
    MemoryItem,
    MemoryCreateRequest,
    DigitalHealthScoreResponse,
    LegacyHandoverRequest,
    CustodianInfo
)
from ..middleware.permissions import get_current_user_id, sanitize_input_text
from ..services.memory_processor import memory_processor
from ..database.firestore_client import db_client

router = APIRouter(prefix="/api/memories", tags=["Memory Vault & Heritage"])


@router.get("/", response_model=List[Dict[str, Any]])
async def list_memories(
    era: Optional[str] = Query(None, description="Filter by era e.g. 1960s"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    limit: int = Query(100, ge=1, le=200),
    user_id: str = Depends(get_current_user_id)
):
    """Retrieves chronological memories for the authenticated user's vault."""
    memories = await db_client.list_memories(user_id=user_id, era=era, tag=tag, limit=limit)
    return memories


@router.post("/", response_model=Dict[str, Any])
async def create_memory(
    req: MemoryCreateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Directly submits a story transcript to be processed by Gemini and persisted."""
    clean_title = sanitize_input_text(req.title)
    clean_text = sanitize_input_text(req.raw_text)

    processed = await memory_processor.process_and_save_memory(
        user_id=user_id,
        title=clean_title,
        raw_transcript=clean_text,
        story_narrative=clean_text,
        language=req.language or "English",
        media_urls=req.media_urls
    )
    return processed


@router.get("/stats/health-score", response_model=DigitalHealthScoreResponse)
async def get_digital_health_score(user_id: str = Depends(get_current_user_id)):
    """Calculates archive completeness percentage and documentation milestones."""
    score = await memory_processor.calculate_health_score(user_id)
    return score


@router.get("/stats/emotion-timeline")
async def get_emotion_timeline(user_id: str = Depends(get_current_user_id)):
    """Provides average Joy, Nostalgia, and Sadness indexed across decades."""
    timeline = await memory_processor.get_emotion_timeline(user_id)
    return timeline


@router.get("/stats/connections")
async def get_memory_connections(user_id: str = Depends(get_current_user_id)):
    """Identifies smart linkages across memories by shared family members and ancestral places."""
    connections = await memory_processor.get_memory_connections(user_id)
    return connections


@router.post("/legacy/custodian", response_model=CustodianInfo)
async def designate_custodian(
    req: LegacyHandoverRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Designates a trusted digital custodian with a 7-day confirmation period."""
    clean_name = sanitize_input_text(req.custodian_name)
    clean_relation = sanitize_input_text(req.relationship)
    now = datetime.utcnow()
    deadline = now + timedelta(days=7)

    custodian = CustodianInfo(
        custodian_name=clean_name,
        custodian_email=req.custodian_email,
        relationship=clean_relation,
        designated_date=now,
        confirmation_due_date=deadline,
        is_confirmed=False,
        status="Pending 7-Day Confirmation"
    )

    await db_client.save_custodian(user_id, custodian.model_dump())
    await db_client.log_audit_event(
        user_id=user_id,
        action="custodian.designated",
        resource_id=user_id,
        metadata={"custodian_email": req.custodian_email, "deadline": deadline.isoformat()}
    )
    return custodian


@router.get("/legacy/custodian", response_model=Optional[CustodianInfo])
async def get_custodian_status(user_id: str = Depends(get_current_user_id)):
    """Retrieves designated custodian information and confirmation timeline."""
    data = await db_client.get_custodian(user_id)
    return data


@router.get("/{memory_id}")
async def get_memory_by_id(
    memory_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Retrieves full details for a single memory card."""
    mem = await db_client.get_memory(memory_id)
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found.")
    if mem.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this memory.")
    return mem


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Permanently deletes a memory from the vault."""
    success = await db_client.delete_memory(memory_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found or unauthorized.")

    await db_client.log_audit_event(
        user_id=user_id,
        action="memory.deleted",
        resource_id=memory_id
    )
    return {"message": "Memory deleted successfully", "id": memory_id}
