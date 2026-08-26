"""
MemoryBox - Elder Mode
Ultra-accessible, large-font, voice-first digital heritage journal designed specifically for seniors.
"""

import streamlit as st
import requests
import os

def get_backend_url():
    candidate = os.getenv("BACKEND_URL", "http://localhost:8000")
    for url in [candidate, "http://localhost:8000", "http://127.0.0.1:8000"]:
        try:
            if requests.get(f"{url}/health", timeout=0.5).status_code == 200:
                return url
        except Exception:
            pass
    return "http://localhost:8000"

BACKEND_URL = get_backend_url()

st.set_page_config(
    page_title="MemoryBox | Elder Mode",
    page_icon="👵",
    layout="wide"
)

# Apply Elder Mode Styling (1.5x font scale, 2x button size, soft soothing warm colors)
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Source+Serif+Pro:ital,wght@0,600;1,400&family=Courier+Prime:wght@700&display=swap');

.stApp {
    background: linear-gradient(180deg, #faf0e6 0%, #f5e6ca 100%);
    color: #5c4033;
    font-family: 'Source Serif Pro', Georgia, serif;
    font-size: 1.6rem !important;
}

h1, h2, h3, .elder-title {
    font-family: 'Playfair Display', serif !important;
    font-style: italic;
    color: #5c4033 !important;
    font-size: 3.2rem !important;
    font-weight: 700;
}

p, span, label, div {
    font-family: 'Source Serif Pro', Georgia, serif;
    color: #5c4033;
    font-size: 1.5rem !important;
    line-height: 1.8;
}

/* Extra Large Paper Card */
.elder-card {
    background: #fffaf0;
    border: 2px solid #d4af37;
    border-radius: 8px;
    box-shadow: 6px 10px 20px rgba(92, 64, 51, 0.08);
    padding: 2.5rem;
    margin-bottom: 2.5rem;
}

/* Double-Sized Friendly Buttons */
.stButton > button {
    background: #fffaf0 !important;
    color: #5c4033 !important;
    border: 2px solid #d4af37 !important;
    border-radius: 8px !important;
    font-family: 'Source Serif Pro', serif !important;
    font-size: 1.8rem !important;
    padding: 1.4rem 3rem !important;
    box-shadow: 4px 6px 14px rgba(92, 64, 51, 0.12) !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover {
    background: #f5e6ca !important;
    border-color: #8c6d1f !important;
}

.stTextInput input, .stTextArea textarea {
    background-color: #fffaf0 !important;
    border: 2px solid #e0d5c1 !important;
    color: #5c4033 !important;
    font-size: 1.5rem !important;
    padding: 1.2rem !important;
    border-radius: 8px !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.markdown("<h1 class='elder-title'>MemoryBox Elder Sanctuary</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-style: italic; color: #7a5c48; font-size: 1.8rem;'>Take your time. There is no rush. Your stories are sacred gifts for your family.</p>", unsafe_allow_html=True)

st.markdown("<hr style='border: none; border-top: 2px solid #d4af37; margin: 1.5rem 0 2.5rem 0;'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="elder-card">
        <h2>🎙️ Tell a Story to Your Family</h2>
        <p>Talk just like you are talking to your grandchild. The app will listen patiently and ask gentle questions about the people, foods, and seasons of your youth.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start Story Session Now", key="start_interview"):
        st.switch_page("pages/interview.py")

with col2:
    st.markdown("""
    <div class="elder-card">
        <h2>📖 Listen to Preserved Memories</h2>
        <p>Revisit the fond moments from the 1960s, festivals in the ancestral home, and memories recorded by your family.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open the Family Vault", key="open_vault"):
        st.switch_page("app.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# Voice / Simple Question Widget
st.markdown("""
<div class="elder-card">
    <h2>💬 Ask Your Family Vault a Question</h2>
    <p>Wondering about a festival, grandmother's recipe, or an old town? Ask below in simple words:</p>
</div>
""", unsafe_allow_html=True)

q = st.text_input("Speak or Type Your Question Here:", placeholder="e.g. What festival did we celebrate in Mysore?")
if st.button("Listen to Answer"):
    if q:
        with st.spinner("Finding your family's memories..."):
            try:
                resp = requests.post(f"{BACKEND_URL}/api/ask/", json={"question": q}, timeout=15)
                if resp.status_code == 200:
                    ans = resp.json()
                    st.markdown(f"""
                    <div class="elder-card" style="background: #fdf6ec;">
                        <span class="elder-title" style="font-size: 2rem;">From Your Vault:</span>
                        <p style="margin-top: 1rem; font-size: 1.6rem; color: #40291e;">{ans.get('answer')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Unable to reach the vault: {e}")
