"""
Navigation Header Component for MemoryBox
Renders the top navigation bar with clean tabs, search shortcut, and feature links.
"""

import streamlit as st
from typing import Callable


def render_navbar(active_tab: str, on_tab_change: Callable[[str], None]):
    """Renders the top navigation tabs."""
    tabs = [
        ("home", "🏠 Home"),
        ("create", "➕ Create Memory"),
        ("ask", "🧠 Ask AI"),
        ("memories", "🗂️ My Memories"),
        ("timeline", "📅 Timeline"),
        ("privacy", "🔐 Privacy")
    ]

    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.5rem; margin-bottom: 0.5rem;">
        <div style="font-family: 'Playfair Display', Georgia, serif; font-weight: 700; font-size: 1.4rem; color: #8b5a2b;">
            📖 Memory Box
        </div>
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.85rem; color: #705342;">
            AI Memory Vault
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(tabs))
    for idx, (tab_id, label) in enumerate(tabs):
        with cols[idx]:
            is_active = (active_tab == tab_id)
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_tab_{tab_id}", type=btn_type, use_container_width=True):
                on_tab_change(tab_id)

    st.markdown("<hr style='margin: 0.8rem 0 1.2rem 0; border: none; border-top: 1px solid #e2d7c5;'>", unsafe_allow_html=True)
