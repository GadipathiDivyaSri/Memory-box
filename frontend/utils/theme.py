"""
Design System and CSS Styling for MemoryBox
Implements a premium 'Digital Memory Vault' aesthetic with warm parchment tones,
gold accents, rounded cards, subtle shadows, and WCAG accessibility standards.
"""

import streamlit as st


def apply_memorybox_theme(is_elder_mode: bool = False):
    """Applies the custom CSS theme and accessibility hooks to the Streamlit app."""
    
    font_scale = "1.35rem" if is_elder_mode else "1.05rem"
    title_scale = "2.8rem" if is_elder_mode else "2.2rem"
    btn_min_height = "64px" if is_elder_mode else "44px"
    btn_font_size = "1.3rem" if is_elder_mode else "1.0rem"
    high_contrast_border = "3px solid #6b4028" if is_elder_mode else "1px solid #e2d7c5"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap');

    /* Global App Background */
    .stApp {{
        background: linear-gradient(180deg, #fbf7f0 0%, #f4ecdf 100%);
        color: #3b2a20;
        font-family: 'Source Serif 4', Georgia, serif;
        font-size: {font_scale};
    }}

    /* Typography */
    h1, h2, h3, .vault-title {{
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #382419 !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }}

    .hero-title {{
        font-size: {title_scale} !important;
        line-height: 1.15 !important;
        margin-bottom: 0.3rem !important;
    }}

    .hero-sub {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #705342 !important;
        font-size: 1.15rem !important;
        line-height: 1.6 !important;
        max-width: 680px;
    }}

    /* Modern Rounded Cards */
    .vault-card {{
        background: #ffffff;
        border: {high_contrast_border};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(74, 52, 38, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .vault-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(74, 52, 38, 0.10);
    }}

    /* Memory Card */
    .memory-card {{
        background: #ffffff;
        border: 1px solid #e7ded0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 3px 14px rgba(74, 52, 38, 0.05);
    }}

    .memory-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }}

    .category-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }}

    .tag-pill {{
        display: inline-block;
        background: #f4ecdf;
        color: #5c4232;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-family: 'Plus Jakarta Sans', sans-serif;
        margin-right: 6px;
        margin-top: 6px;
    }}

    /* Stat Cards */
    .metric-card {{
        background: #ffffff;
        border: 1px solid #e5dbcb;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }}

    .metric-num {{
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #8b5a2b;
        line-height: 1;
    }}

    .metric-label {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        color: #7a6352;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 6px;
    }}

    /* Memory Worth Reliving (Hero Card) */
    .relive-card {{
        background: linear-gradient(135deg, #fffdfa 0%, #fdf8ee 100%);
        border: 2px solid #d4af37;
        border-radius: 18px;
        padding: 26px;
        box-shadow: 0 6px 24px rgba(212, 175, 55, 0.15);
        margin-bottom: 24px;
    }}

    /* Flow Steps: Capture -> Understand -> Organize -> Search -> Relive */
    .flow-step-box {{
        background: #ffffff;
        border: 1px solid #e8decb;
        border-radius: 12px;
        padding: 14px 10px;
        text-align: center;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    .flow-step-icon {{
        font-size: 1.6rem;
        margin-bottom: 4px;
    }}

    .flow-step-title {{
        font-weight: 700;
        font-size: 0.95rem;
        color: #3b2a20;
    }}

    .flow-step-desc {{
        font-size: 0.78rem;
        color: #7a6352;
        line-height: 1.3;
    }}

    /* Button Polish */
    .stButton > button {{
        min-height: {btn_min_height};
        font-size: {btn_font_size} !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        border: 1px solid #8b5a2b !important;
        background: #ffffff;
        color: #4a2e1b !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        transition: all 0.15s ease-in-out;
    }}

    .stButton > button:hover {{
        background: #8b5a2b !important;
        color: #ffffff !important;
        border-color: #8b5a2b !important;
        box-shadow: 0 4px 12px rgba(139, 90, 43, 0.25);
    }}

    /* Primary CTA Button */
    div[data-testid="stVerticalBlock"] > div > button[kind="primary"] {{
        background: #8b5a2b !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
    }}

    /* Inputs */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        background: #ffffff !important;
        border: 1px solid #d9ccb9 !important;
        border-radius: 8px !important;
        color: #3b2a20 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}

    /* Top Navigation bar */
    .navbar-container {{
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid #eae0d0;
        border-radius: 14px;
        padding: 10px 20px;
        margin-bottom: 24px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }}

    /* Accessibility ARIA helper */
    .sr-only {{
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Injected ARIA and Keyboard Navigation Listener
    st.markdown("""
    <!-- ARIA Live Region for Screen Readers -->
    <div id="memorybox-aria-live" aria-live="polite" style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0);">
        MemoryBox Personal AI Vault Active
    </div>

    <!-- Keyboard Navigation Script (Ctrl+Enter to submit active form/button) -->
    <script>
    (function() {
        if (window._mb_kbd_installed) return;
        window._mb_kbd_installed = true;
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const submitBtn = document.querySelector('button[kind="primary"]') || 
                                  document.querySelector('.stButton button');
                if (submitBtn) {
                    submitBtn.focus();
                    submitBtn.click();
                }
            }
        });
    })();
    </script>
    """, unsafe_allow_html=True)
