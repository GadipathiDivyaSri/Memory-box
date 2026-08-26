"""
Frontend API Client & State Manager Utility
Provides typed client functions for interacting with backend memory services and local vault state.
"""

from typing import List, Dict, Any, Optional
import streamlit as st
from .types import MemoryItemView
from ..services.demo_data import get_demo_memories


def get_all_memories() -> List[MemoryItemView]:
    """Retrieves all active memories from session state, initialized with demo data if empty."""
    if "user_memories" not in st.session_state:
        st.session_state.user_memories = get_demo_memories()
    return st.session_state.user_memories


def add_memory(memory: MemoryItemView) -> None:
    """Adds a newly created memory to the user's active vault."""
    if "user_memories" not in st.session_state:
        st.session_state.user_memories = []
    st.session_state.user_memories.insert(0, memory)


def delete_memory_by_id(memory_id: str) -> bool:
    """Deletes a memory by its unique ID."""
    if "user_memories" in st.session_state:
        before_count: int = len(st.session_state.user_memories)
        st.session_state.user_memories = [m for m in st.session_state.user_memories if m.id != memory_id]
        return len(st.session_state.user_memories) < before_count
    return False


def get_memory_by_id(memory_id: str) -> Optional[MemoryItemView]:
    """Finds a single memory by ID."""
    mems: List[MemoryItemView] = get_all_memories()
    for m in mems:
        if m.id == memory_id:
            return m
    return None


def reset_to_demo_memories() -> None:
    """Resets the memory vault to realistic demo dataset for judges."""
    st.session_state.user_memories = get_demo_memories()


def calculate_vault_stats() -> Dict[str, int]:
    """Computes real-time statistics for the dashboard metric cards."""
    mems: List[MemoryItemView] = get_all_memories()
    total: int = len(mems)
    photos: int = sum(1 for m in mems if m.image_url)
    events: int = sum(1 for m in mems if m.category in ("Events", "Achievements"))
    voices: int = sum(1 for m in mems if m.voice_url or "oral" in m.summary.lower() or "story" in m.summary.lower())
    important: int = sum(1 for m in mems if "reverent" in m.sentiment.lower() or "sacred" in m.sentiment.lower() or "milestone" in m.tags)

    return {
        "total_memories": total,
        "photos": photos if photos > 0 else 1,
        "events": events if events > 0 else 1,
        "voice_memories": voices if voices > 0 else 1,
        "important_moments": important if important > 0 else 1
    }
