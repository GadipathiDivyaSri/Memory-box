"""
Memory Card and Detail View Components for MemoryBox
Renders attractive cards, the 'Memory Worth Reliving' showcase, and full inspection details.
"""

import streamlit as st
from typing import Optional, Callable
from ..utils.types import MemoryItemView


def get_category_color(category: str) -> str:
    palette = {
        "Family": "#e11d48",       # Rose / Coral
        "Travel": "#0284c7",       # Ocean Blue
        "College": "#7c3aed",      # Purple / Violet
        "Achievements": "#d97706", # Rich Gold / Amber
        "Events": "#9333ea",       # Royal Purple
        "Friends": "#059669",      # Emerald Green
        "Everyday": "#475569",     # Modern Slate
        "Work": "#2563eb"          # Vibrant Blue
    }
    return palette.get(category, "#4f46e5")


def render_memory_of_the_day(memory: Optional[MemoryItemView], on_relive_click: Optional[Callable[[str], None]] = None):
    """Renders the featured 'Memory Worth Reliving' card on the dashboard."""
    if not memory:
        return

    st.markdown("""
    <div style="margin-top: 1.5rem; margin-bottom: 0.5rem;">
        <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #b8860b; font-weight: 700;">
            ✨ Memory Worth Reliving
        </span>
    </div>
    """, unsafe_allow_html=True)

    cat_color = get_category_color(memory.category)

    with st.container():
        st.markdown(f"""
        <div class="relive-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span class="category-badge" style="background: {cat_color}18; color: {cat_color}; border: 1px solid {cat_color}40;">
                        {memory.category}
                    </span>
                    <span style="color: #7a6352; font-size: 0.88rem; margin-left: 10px; font-family: 'Plus Jakarta Sans', sans-serif;">
                        🗓️ {memory.date} &nbsp;·&nbsp; 📍 {memory.location}
                    </span>
                </div>
                <div style="font-size: 1.3rem;">✨</div>
            </div>
            <h3 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.65rem; color: #3b2a20; margin: 0.8rem 0 0.4rem 0;">
                {memory.title}
            </h3>
            <p style="color: #5c4232; font-size: 1.05rem; line-height: 1.6; margin-bottom: 0.8rem;">
                "{memory.summary}"
            </p>
            <div style="margin-bottom: 0.6rem;">
                {' '.join([f'<span class="tag-pill">#{t}</span>' for t in memory.tags[:4]])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Relive Memory: {memory.title} →", key=f"relive_btn_{memory.id}", use_container_width=True):
            if on_relive_click:
                on_relive_click(memory.id)


def render_memory_card(memory: MemoryItemView, on_select: Optional[Callable[[str], None]] = None):
    """Renders a visually attractive, concise memory card."""
    cat_color = get_category_color(memory.category)
    tags_html = " ".join([f"<span class='tag-pill'>#{t}</span>" for t in memory.tags[:3]])
    people_str = f"👥 {', '.join(memory.people[:2])}" if memory.people else ""

    st.markdown(f"""
    <div class="memory-card">
        <div class="memory-card-header">
            <span class="category-badge" style="background: {cat_color}15; color: {cat_color}; border: 1px solid {cat_color}35;">
                {memory.category}
            </span>
            <span style="color: #8c7869; font-size: 0.82rem; font-family: 'Plus Jakarta Sans', sans-serif;">
                {memory.date}
            </span>
        </div>
        <h4 style="font-family: 'Playfair Display', Georgia, serif; color: #3b2a20; font-size: 1.25rem; margin: 0.4rem 0 0.3rem 0; line-height: 1.3;">
            {memory.title}
        </h4>
        <p style="color: #614c3e; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0.6rem;">
            {memory.summary}
        </p>
        <div style="font-size: 0.82rem; color: #7a6352; margin-bottom: 0.5rem; font-family: 'Plus Jakarta Sans', sans-serif;">
            📍 {memory.location} &nbsp;&nbsp; {people_str}
        </div>
        <div>
            {tags_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"View Memory →", key=f"card_open_{memory.id}", use_container_width=True):
        if on_select:
            on_select(memory.id)


def render_memory_detail_view(
    memory: MemoryItemView,
    on_back: Callable[[], None],
    on_delete: Optional[Callable[[str], None]] = None
):
    """Renders the full memory detail view with AI reflection and action buttons."""
    cat_color = get_category_color(memory.category)

    # Top Bar with Back Button
    c_b1, c_b2 = st.columns([1, 4])
    with c_b1:
        if st.button("← Back", use_container_width=True, key="detail_back_btn"):
            on_back()

    st.markdown(f"""
    <div class="vault-card" style="margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
            <span class="category-badge" style="background: {cat_color}20; color: {cat_color}; border: 1px solid {cat_color}50; font-size: 0.9rem;">
                {memory.category}
            </span>
            <span style="color: #7a6352; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.9rem;">
                🗓️ {memory.date} &nbsp;·&nbsp; 📍 {memory.location}
            </span>
        </div>
        <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.1rem; color: #3b2a20; margin-bottom: 0.8rem;">
            {memory.title}
        </h2>
    """, unsafe_allow_html=True)

    if memory.image_url:
        st.image(memory.image_url, use_container_width=True, caption=memory.title)

    st.markdown(f"""
        <div style="background: #fdfbf7; border-left: 3px solid #d4af37; padding: 1rem; border-radius: 4px; margin: 1.2rem 0;">
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 0.82rem; text-transform: uppercase; color: #8b5a2b; letter-spacing: 0.05em; margin-bottom: 0.3rem;">
                AI Summary
            </div>
            <div style="color: #3b2a20; font-size: 1.05rem; line-height: 1.6;">
                {memory.summary}
            </div>
        </div>

        <h4 style="font-family: 'Playfair Display', Georgia, serif; color: #3b2a20; margin-top: 1.2rem;">Full Memory Narrative</h4>
        <p style="color: #4a382d; font-size: 1.08rem; line-height: 1.7; white-space: pre-wrap;">
            {memory.description or memory.raw_text}
        </p>
    """, unsafe_allow_html=True)

    # Why this memory matters (AI Reflection)
    if memory.why_it_matters:
        st.markdown(f"""
        <div style="background: #fffdf7; border: 1px dashed #d4af37; border-radius: 12px; padding: 1.2rem; margin: 1.5rem 0;">
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 0.85rem; color: #8b5a2b; margin-bottom: 0.3rem;">
                💡 Why this memory matters
            </div>
            <div style="color: #5c4232; font-style: italic; font-size: 1.02rem; line-height: 1.5;">
                "{memory.why_it_matters}"
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Metadata badges
    st.markdown("""<div style="margin-top: 1rem;">""", unsafe_allow_html=True)
    if memory.people:
        st.markdown(f"**People Present:** {', '.join(memory.people)}")
    if memory.sentiment:
        st.markdown(f"**Emotional Tone:** *{memory.sentiment}*")
    st.markdown(f"**Tags:** {' '.join([f'`#{t}`' for t in memory.tags])}")
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Action Row: Delete & Back
    col_act1, col_act2 = st.columns([3, 1])
    with col_act2:
        if st.button("🗑️ Delete Memory", key=f"del_btn_{memory.id}", use_container_width=True):
            if on_delete:
                on_delete(memory.id)
