"""
Design System and CSS Styling for MemoryBox
Implements a clean, modern, high-contrast 'AI Memory Vault' aesthetic with
crisp slate tones, vibrant indigo & blue accents, polished cards, and WCAG accessibility standards.
"""

import streamlit as st


def apply_memorybox_theme(is_elder_mode: bool = False):
    """Applies the custom CSS theme and accessibility hooks to the Streamlit app."""
    
    font_scale = "1.35rem" if is_elder_mode else "1.02rem"
    title_scale = "2.8rem" if is_elder_mode else "2.4rem"
    btn_min_height = "60px" if is_elder_mode else "42px"
    btn_font_size = "1.3rem" if is_elder_mode else "0.95rem"
    card_border = "3px solid #1e293b" if is_elder_mode else "1px solid #e2e8f0"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');

    /* Global App Background - Modern Clean Slate */
    .stApp {{
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1e293b;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: {font_scale};
    }}

    /* Typography */
    h1, h2, h3, .vault-title {{
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }}

    .hero-title {{
        font-size: {title_scale} !important;
        line-height: 1.15 !important;
        margin-bottom: 0.3rem !important;
        color: #0f172a !important;
    }}

    .hero-sub {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #475569 !important;
        font-size: 1.15rem !important;
        line-height: 1.6 !important;
        max-width: 680px;
    }}

    /* Modern Rounded Elevated Cards */
    .vault-card {{
        background: #ffffff;
        border: {card_border};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .vault-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.10);
    }}

    /* Memory Card */
    .memory-card {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
        transition: all 0.2s ease;
    }}

    .memory-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 24px -4px rgba(15, 23, 42, 0.08);
        border-color: #cbd5e1;
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
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 500;
        margin-right: 6px;
        margin-top: 6px;
    }}

    /* Stat Cards */
    .metric-card {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 14px -2px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s ease;
    }}

    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -2px rgba(15, 23, 42, 0.08);
    }}

    .metric-num {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #4f46e5;
        line-height: 1;
    }}

    .metric-label {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 6px;
    }}

    /* Memory Worth Reliving (Hero Card) */
    .relive-card {{
        background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%);
        border: 1.5px solid #c7d2fe;
        border-radius: 18px;
        padding: 26px;
        box-shadow: 0 8px 28px -4px rgba(79, 70, 229, 0.12);
        margin-bottom: 24px;
    }}

    /* Flow Steps: Capture -> Understand -> Organize -> Search -> Relive */
    .flow-step-box {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 12px;
        text-align: center;
        font-family: 'Plus Jakarta Sans', sans-serif;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}

    .flow-step-icon {{
        font-size: 1.8rem;
        margin-bottom: 6px;
    }}

    .flow-step-title {{
        font-weight: 700;
        font-size: 0.95rem;
        color: #0f172a;
    }}

    .flow-step-desc {{
        font-size: 0.8rem;
        color: #64748b;
        line-height: 1.4;
    }}

    /* Button Polish */
    .stButton > button {{
        min-height: {btn_min_height};
        font-size: {btn_font_size} !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        background: #ffffff;
        color: #1e293b !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        transition: all 0.15s ease-in-out;
    }}

    .stButton > button:hover {{
        background: #f8fafc !important;
        color: #4f46e5 !important;
        border-color: #6366f1 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
    }}

    /* Primary Action Button - Vibrant Indigo Gradient */
    div[data-testid="stVerticalBlock"] > div > button[kind="primary"],
    button[type="submit"][kind="primary"],
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
    }}

    div[data-testid="stVerticalBlock"] > div > button[kind="primary"]:hover,
    button[type="submit"][kind="primary"]:hover,
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #4338ca 0%, #2563eb 100%) !important;
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.45) !important;
        transform: translateY(-1px);
    }}

    /* Inputs & Textareas */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        color: #0f172a !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    }}

    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {{
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }}

    /* Top Navigation bar */
    .navbar-container {{
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 10px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
    }}

    /* Timeline Styling */
    .timeline-node {{
        border-left: 3px solid #6366f1;
        padding-left: 20px;
        margin-left: 12px;
        position: relative;
        padding-bottom: 24px;
    }}

    .timeline-dot {{
        position: absolute;
        left: -8px;
        top: 0;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #4f46e5;
        border: 2px solid #ffffff;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
    }}

    /* Scrollbars */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: #f1f5f9;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #cbd5e1;
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #94a3b8;
    }}
    </style>
    """, unsafe_allow_html=True)
