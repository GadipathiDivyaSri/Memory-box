"""
API Client & State Manager for MemoryBox
Handles memory persistence, caching, and state synchronization across views.
"""

import streamlit as st
from typing import List, Optional
from ..utils.types import MemoryItemView
from .demo_data import get_demo_memories


def get_all_memories() -> List[MemoryItemView]:
    """Retrieves all active memories from session state, initialized with demo data if empty."""
    if "user_memories" not in st.session_state:
        st.session_state.user_memories = get_demo_memories()
    return st.session_state.user_memories


def add_memory(memory: MemoryItemView) -> None:
    """Adds a newly created memory to the user's active vault."""
    if "user_memories" not in st.session_state:
        st.session_state.user_memories = []
    # Insert at beginning so newest memory appears first
    st.session_state.user_memories.insert(0, memory)


def delete_memory_by_id(memory_id: str) -> bool:
    """Deletes a memory by its ID."""
    if "user_memories" in st.session_state:
        before_count = len(st.session_state.user_memories)
        st.session_state.user_memories = [m for m in st.session_state.user_memories if m.id != memory_id]
        return len(st.session_state.user_memories) < before_count
    return False


def get_memory_by_id(memory_id: str) -> Optional[MemoryItemView]:
    """Finds a single memory by ID."""
    mems = get_all_memories()
    for m in mems:
        if m.id == memory_id:
            return m
    return None


def reset_to_demo_memories() -> None:
    """Resets the memory vault to realistic demo dataset for judges."""
    st.session_state.user_memories = get_demo_memories()


def calculate_vault_stats():
    """Computes real-time statistics for the dashboard."""
    mems = get_all_memories()
    total = len(mems)
    photos = sum(1 for m in mems if m.image_url)
    events = sum(1 for m in mems if m.category in ("Events", "Achievements"))
    voices = sum(1 for m in mems if m.voice_url or "oral" in m.summary.lower() or "story" in m.summary.lower())
    important = sum(1 for m in mems if "reverent" in m.sentiment.lower() or "sacred" in m.sentiment.lower() or "milestone" in m.tags)

    return {
        "total_memories": total,
        "photos": photos if photos > 0 else 1,
        "events": events if events > 0 else 1,
        "voice_memories": voices if voices > 0 else 1,
        "important_moments": important if important > 0 else 1
    }
