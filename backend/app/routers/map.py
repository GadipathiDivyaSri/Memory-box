"""
Heritage Map Router
Endpoints for geographical story visualization, ancestral migrations, and coordinates.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from ..middleware.permissions import get_current_user_id
from ..database.firestore_client import db_client

router = APIRouter(prefix="/api/map", tags=["Heritage Map"])

# Standard geo coordinates for ancestral heritage centers if not geocoded
GEO_DEFAULTS = {
    "mysore": (12.2958, 76.6394),
    "thanjavur": (10.7870, 79.1378),
    "chennai": (13.0827, 80.2707),
    "madras": (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867),
    "kolkata": (22.5726, 88.3639),
    "varanasi": (25.3176, 82.9739),
    "delhi": (28.6139, 77.2090),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946)
}


@router.get("/points", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
async def get_map_points(
    user_id: str = Depends(get_current_user_id)
):
    """
    Returns memories with geographic coordinates for map plotting.
    """
    memories = await db_client.list_memories(user_id=user_id, limit=200)
    points = []

    for m in memories:
        lat = m.get("latitude")
        lon = m.get("longitude")
        loc = m.get("location_name", "Ancestral Homeland")

        if not lat or not lon:
            loc_lower = str(loc).lower()
            for key, coords in GEO_DEFAULTS.items():
                if key in loc_lower:
                    lat, lon = coords
                    break

        if lat and lon:
            points.append({
                "id": m.get("id"),
                "title": m.get("title", "Oral Story"),
                "era": m.get("era", "1960s"),
                "year": m.get("year", 1965),
                "location_name": loc,
                "latitude": float(lat),
                "longitude": float(lon),
                "narrative": (m.get("story_narrative") or m.get("raw_transcript", ""))[:140] + "...",
                "people_involved": m.get("people_involved", []),
                "cultural_traditions": m.get("cultural_traditions", [])
            })

    return points


@router.get("/migrations")
async def get_ancestral_migrations(
    user_id: str = Depends(get_current_user_id)
):
    """
    Traces migration paths connecting places across consecutive decades.
    """
    points = await get_map_points(user_id=user_id)
    # Sort chronologically
    sorted_pts = sorted(points, key=lambda p: p.get("year", 1970))
    paths = []
    for i in range(len(sorted_pts) - 1):
        paths.append({
            "from": sorted_pts[i]["location_name"],
            "to": sorted_pts[i+1]["location_name"],
            "from_coords": [sorted_pts[i]["longitude"], sorted_pts[i]["latitude"]],
            "to_coords": [sorted_pts[i+1]["longitude"], sorted_pts[i+1]["latitude"]],
            "years": f"{sorted_pts[i].get('year')} → {sorted_pts[i+1].get('year')}"
        })

    return {
        "user_id": user_id,
        "migration_count": len(paths),
        "paths": paths
    }
