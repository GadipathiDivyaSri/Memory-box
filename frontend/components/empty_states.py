"""
Empty States Component for MemoryBox
Ensures zero blank screens with helpful onboarding guidance and action triggers.
"""

import streamlit as st
from typing import Optional, Callable


def render_empty_vault(on_create_click: Optional[Callable[[], None]] = None, on_demo_click: Optional[Callable[[], None]] = None):
    """Renders warm empty state when vault has 0 memories."""
    st.markdown("""
    <div style="text-align: center; background: #ffffff; border: 2px dashed #d9ccb9; border-radius: 16px; padding: 3rem 1.5rem; margin: 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.8rem;">📦</div>
        <h3 style="font-family: 'Playfair Display', Georgia, serif; color: #3b2a20; margin-bottom: 0.5rem;">
            Your memory box is waiting for its first story.
        </h3>
        <p style="color: #705342; font-size: 1.05rem; max-width: 500px; margin: 0 auto 1.5rem auto; line-height: 1.5;">
            Add your first memory and let AI organize it for you, or load our realistic demo dataset to experience the platform immediately.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_b1, c_b2 = st.columns(2)
    with c_b1:
        if st.button("➕ Create Memory", type="primary", use_container_width=True, key="empty_create_btn"):
            if on_create_click:
                on_create_click()
    with c_b2:
        if st.button("✨ Explore Demo Memories", use_container_width=True, key="empty_demo_btn"):
            if on_demo_click:
                on_demo_click()


def render_empty_search(query: str):
    """Renders helpful state when search yields no matches."""
    st.markdown(f"""
    <div style="text-align: center; background: #ffffff; border: 1px solid #e2d7c5; border-radius: 14px; padding: 2.5rem 1rem; margin: 1.5rem 0;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</div>
        <h4 style="font-family: 'Playfair Display', Georgia, serif; color: #3b2a20; margin-bottom: 0.3rem;">
            No memories found for "{query}"
        </h4>
        <p style="color: #705342; font-size: 0.95rem; max-width: 460px; margin: 0 auto; line-height: 1.5;">
            Try asking about family members (e.g. <i>'Grandmother'</i>), places (<i>'Mysore'</i>), or years (<i>'2025'</i>).
        </p>
    </div>
    """, unsafe_allow_html=True)
