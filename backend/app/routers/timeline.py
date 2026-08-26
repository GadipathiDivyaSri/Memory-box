"""
Timeline Router
Endpoints for generational timeline visualization, decade groupings, and life milestone tracking.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from ..middleware.permissions import get_current_user_id
from ..database.firestore_client import db_client

router = APIRouter(prefix="/api/timeline", tags=["Generational Timeline"])


@router.get("/", response_model=List[Dict[str, Any]])
async def get_timeline_events(
    user_id: str = Depends(get_current_user_id),
    sort: str = Query("asc", pattern="^(asc|desc)$")
):
    """
    Returns all memories arranged chronologically by year/era for the timeline visualization.
    """
    memories = await db_client.list_memories(user_id=user_id, limit=200)

    # Sort memories by year (or era as fallback)
    def parse_year(m):
        y = m.get("year")
        if isinstance(y, int):
            return y
        if isinstance(y, str) and y.isdigit():
            return int(y)
        era = str(m.get("era", ""))
        for token in era.split():
            clean = token.replace("s", "")
            if clean.isdigit():
                return int(clean)
        return 1970

    sorted_memories = sorted(memories, key=parse_year, reverse=(sort == "desc"))
    return sorted_memories


@router.get("/eras")
async def get_era_breakdown(
    user_id: str = Depends(get_current_user_id)
):
    """
    Returns counts of memories grouped by decade / historical era.
    """
    memories = await db_client.list_memories(user_id=user_id, limit=200)
    eras: Dict[str, int] = {}
    for m in memories:
        era = m.get("era") or "Undated"
        eras[era] = eras.get(era, 0) + 1

    return {
        "total_memories": len(memories),
        "eras": eras
    }
