"""
Statistics & Metrics Component for MemoryBox Dashboard
Renders attractive metric cards:
- Total Memories
- Photos
- Events
- Voice Memories
- Important Moments
"""

import streamlit as st
from typing import Dict, Any


def render_dashboard_stats(stats: Dict[str, Any]):
    """Renders 5 attractive metric cards summarizing the memory vault."""
    total = stats.get("total_memories", 0)
    photos = stats.get("photos", 0)
    events = stats.get("events", 0)
    voices = stats.get("voice_memories", 0)
    important = stats.get("important_moments", 0)

    st.markdown("""
    <div style="margin-bottom: 0.5rem; margin-top: 1rem;">
        <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; color: #4f46e5; font-weight: 700;">
            Vault Overview
        </span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-num">{total}</div>
            <div class="metric-label">Total Memories</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-num">{photos}</div>
            <div class="metric-label">Photos</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-num">{events}</div>
            <div class="metric-label">Events</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-num">{voices}</div>
            <div class="metric-label">Voice Memories</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-num">{important}</div>
            <div class="metric-label">Key Moments</div>
        </div>
        """, unsafe_allow_html=True)
