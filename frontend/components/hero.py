"""
Hero & Welcome Banner Component for MemoryBox
Communicates core positioning:
"Memory Box: Your memories. Understood by AI.
Capture your moments, let AI organize them, and rediscover meaningful memories instantly."
"""

import streamlit as st


def render_hero_section(on_create_click=None, on_explore_click=None):
    """Renders the main hero section with headline, value proposition, and CTAs."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem 1.5rem 1rem;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 68px; height: 68px; background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%); border: 1.5px solid #c7d2fe; border-radius: 22px; font-size: 2.2rem; margin-bottom: 1rem; box-shadow: 0 4px 20px rgba(79, 70, 229, 0.15);">
            📖
        </div>
        <h1 class="hero-title">Memory Box</h1>
        <h3 style="font-family: 'Plus Jakarta Sans', sans-serif !important; color: #4f46e5; font-weight: 700; font-size: 1.5rem; margin-top: -0.5rem; margin-bottom: 0.8rem; letter-spacing: -0.01em;">
            Your memories. Understood by AI.
        </h3>
        <p class="hero-sub" style="margin: 0 auto 1.5rem auto;">
            Capture your moments, let AI organize them, and rediscover meaningful memories instantly.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Primary & Secondary Call to Action Row
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button(
                "➕ Create Memory",
                type="primary",
                use_container_width=True,
                key="hero_cta_create",
                help="AI will automatically generate a title, summary, and tags for you."
            ):
                if on_create_click:
                    on_create_click()
        with c_btn2:
            if st.button(
                "✨ Explore My Memories",
                use_container_width=True,
                key="hero_cta_explore",
                help="Search your personal memory vault naturally."
            ):
                if on_explore_click:
                    on_explore_click()


def render_how_it_works():
    """Renders the 'How It Works' 4-step visual flow: Capture -> AI Understands -> Organize -> Rediscover."""
    st.markdown("""
    <div style="margin-top: 2rem; margin-bottom: 2rem;">
        <div style="text-align: center; margin-bottom: 1.2rem;">
            <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; color: #8b5a2b; font-weight: 700;">
                The Memory Engine
            </span>
            <h4 style="font-family: 'Playfair Display', Georgia, serif; color: #3b2a20; margin: 0.2rem 0;">
                How Memory Box Works
            </h4>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="flow-step-box">
            <div class="flow-step-icon">📸</div>
            <div class="flow-step-title">1. Capture</div>
            <div class="flow-step-desc">Save a photo, voice note, or simple written story.</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="flow-step-box">
            <div class="flow-step-icon">🧠</div>
            <div class="flow-step-title">2. AI Understands</div>
            <div class="flow-step-desc">AI extracts people, places, dates, emotions & meaning.</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="flow-step-box">
            <div class="flow-step-icon">🗂️</div>
            <div class="flow-step-title">3. Organize</div>
            <div class="flow-step-desc">Auto-categorized by smart themes and timelines.</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="flow-step-box">
            <div class="flow-step-icon">🔍</div>
            <div class="flow-step-title">4. Rediscover</div>
            <div class="flow-step-desc">Ask questions naturally and relive precious moments.</div>
        </div>
        """, unsafe_allow_html=True)
