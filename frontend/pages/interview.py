"""
MemoryBox - Relentless AI Interviewer Studio
Dedicated Letters-layout conversational interface where the empathetic AI historian
gently draws out multi-sensory ancestral memories through focused follow-up questions.
"""

import streamlit as st
import requests
import os
import json
from datetime import datetime

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
    page_title="MemoryBox | AI Oral Interviewer",
    page_icon="🎙️",
    layout="wide"
)

# Apply Clean Vintage Styles & Letters Layout
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600;1,700&family=Source+Serif+Pro:ital,wght@0,400;0,600;1,400&family=Courier+Prime:wght@400;700&display=swap');

.stApp {
    background: linear-gradient(180deg, #faf0e6 0%, #f5e6ca 100%);
    color: #5c4033;
    font-family: 'Source Serif Pro', Georgia, serif;
    font-size: 1.1rem;
}

h1, h2, h3, .vintage-title {
    font-family: 'Playfair Display', serif !important;
    font-style: italic;
    color: #5c4033 !important;
    font-weight: 700;
}

/* Letters Layout for Conversation */
.letter-row {
    display: flex;
    margin-bottom: 1.5rem;
    width: 100%;
}

/* Historian / AI: Left Side (Lighter Cream) */
.historian-letter {
    background: #fffaf0;
    border: 1px solid #e0d5c1;
    border-left: 4px solid #d4af37;
    border-radius: 8px;
    padding: 1.5rem;
    max-width: 82%;
    margin-right: auto;
    box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.04);
}

/* User / Elder: Right Side (Slightly Darker Beige) */
.elder-letter {
    background: #eddcc6;
    border: 1px solid #dcbe9d;
    border-right: 4px solid #8c6d1f;
    border-radius: 8px;
    padding: 1.5rem;
    max-width: 82%;
    margin-left: auto;
    box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.04);
}

/* Follow-up Question Cards / Chips */
.question-chip {
    background: #fffdfa;
    border: 1px dashed #d4af37;
    border-radius: 6px;
    padding: 0.85rem 1.2rem;
    margin: 0.5rem 0;
    cursor: pointer;
    font-size: 1.05rem;
    color: #5c4033;
    transition: all 0.2s ease;
}
.question-chip:hover {
    background: #f8eedb;
    border-color: #8c6d1f;
}

.stButton > button {
    background: #fffaf0 !important;
    color: #5c4033 !important;
    border: 1px solid #d4af37 !important;
    border-radius: 4px !important;
    font-family: 'Source Serif Pro', serif !important;
    font-size: 1.05rem !important;
    padding: 0.7rem 1.5rem !important;
    box-shadow: 2px 3px 6px rgba(92, 64, 51, 0.08) !important;
}
.stButton > button:hover {
    background: #f5e6ca !important;
    border-color: #8c6d1f !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# State initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "interview_messages" not in st.session_state:
    st.session_state.interview_messages = []
if "current_questions" not in st.session_state:
    st.session_state.current_questions = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 1
if "interview_finished" not in st.session_state:
    st.session_state.interview_finished = False
if "final_story" not in st.session_state:
    st.session_state.final_story = None


# --- Top Header ---
c_h1, c_h2 = st.columns([3, 1])
with c_h1:
    st.markdown("<h1>The Relentless AI Interviewer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-style: italic; color: #7a5c48;'>Like a curious, patient grandchild who wants to know every detail of how the past tasted, smelled, and felt.</p>", unsafe_allow_html=True)
with c_h2:
    if st.button("← Return to Vault", use_container_width=True):
        st.switch_page("app.py")

st.markdown("<hr style='border: none; border-top: 1px solid #d4af37; margin: 1rem 0 2rem 0;'>", unsafe_allow_html=True)


# ==============================================================================
# PHASE 1: KICKOFF
# ==============================================================================
if not st.session_state.session_id:
    st.markdown("""
    <div class="historian-letter" style="max-width: 100%; margin-bottom: 2rem;">
        <span class="vintage-title" style="font-size: 1.4rem;">Dearest Grandparent,</span>
        <p style="margin-top: 0.8rem; font-size: 1.15rem; line-height: 1.8;">
            I would love to hear a memory from your life. It can be anything—a festival morning, the scent of the first rain, the taste of a dish your mother cooked, or a quiet walk with someone you loved. Where shall we begin?
        </p>
    </div>
    """, unsafe_allow_html=True)

    initial_prompt = st.text_input(
        "Opening thought or topic:",
        value="I want to tell a story about the monsoon festivals in our ancestral village.",
        placeholder="e.g. I remember my father bringing home our first radio in 1965..."
    )

    if st.button("Begin the Memory Journey 🎙️", use_container_width=True):
        with st.spinner("Preparing our interview session..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/interview/start",
                    json={"initial_thought": initial_prompt, "language": "English"},
                    timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.session_id = data.get("session_id")
                    st.session_state.current_questions = data.get("current_questions", [])
                    st.session_state.turn_count = 1
                    st.session_state.interview_finished = False

                    # Append initial messages
                    st.session_state.interview_messages = [
                        {
                            "sender": "elder",
                            "text": initial_prompt
                        },
                        {
                            "sender": "historian",
                            "text": "Thank you for opening this door into the past. To help me picture this vividly:",
                            "questions": st.session_state.current_questions
                        }
                    ]
                    st.rerun()
                else:
                    st.error("Could not start interview session. Please ensure the backend is running.")
            except Exception as e:
                st.error(f"Connection error: {e}")

# ==============================================================================
# PHASE 2 & 3: THE LETTERS CONVERSATION LOOP
# ==============================================================================
else:
    # Progress indicator
    turns_left = 8 - st.session_state.turn_count + 1
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1.5rem;">
        <span class="vintage-mono" style="color: #8c6d1f; font-weight: 700;">Turn {st.session_state.turn_count} of 8</span>
        <span class="vintage-mono" style="color: #7a5c48;">Session ID: {st.session_state.session_id}</span>
    </div>
    """, unsafe_allow_html=True)

    # Render Conversation in "Letters" format
    for msg in st.session_state.interview_messages:
        if msg["sender"] == "elder":
            st.markdown(f"""
            <div class="letter-row">
                <div class="elder-letter">
                    <strong class="vintage-title" style="font-size: 1.15rem; color: #5c4033;">Elder:</strong>
                    <p style="margin-top: 0.5rem; font-size: 1.1rem; line-height: 1.7;">{msg['text']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            questions_html = ""
            if msg.get("questions"):
                questions_html = "<div style='margin-top: 0.8rem;'>"
                for q_idx, q in enumerate(msg["questions"], start=1):
                    questions_html += f"""
                    <div class="question-chip">
                        <strong>Q{q_idx}:</strong> {q}
                    </div>
                    """
                questions_html += "</div>"

            st.markdown(f"""
            <div class="letter-row">
                <div class="historian-letter">
                    <strong class="vintage-title" style="font-size: 1.15rem; color: #8c6d1f;">Gentle Historian:</strong>
                    <p style="margin-top: 0.5rem; font-size: 1.1rem; line-height: 1.7;">{msg['text']}</p>
                    {questions_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Response Input Area (if not finished)
    if not st.session_state.interview_finished:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Your Response:")
        elder_reply = st.text_area(
            "Share what you remember (or type 'That's all' when finished):",
            placeholder="Describe what you smelled, heard, or felt, or answer any of the questions above...",
            height=120
        )

        col_b1, col_b2 = st.columns([3, 1])
        with col_b1:
            if st.button("Send Response 📜", use_container_width=True):
                if elder_reply.strip():
                    with st.spinner("Listening with love and crafting the next follow-up questions..."):
                        try:
                            resp = requests.post(
                                f"{BACKEND_URL}/api/interview/respond",
                                json={
                                    "session_id": st.session_state.session_id,
                                    "user_response": elder_reply
                                },
                                timeout=20
                            )
                            if resp.status_code == 200:
                                res_data = resp.json()
                                # Add user message
                                st.session_state.interview_messages.append({
                                    "sender": "elder",
                                    "text": elder_reply
                                })

                                should_finish = res_data.get("should_finish", False)
                                if should_finish:
                                    st.session_state.interview_finished = True
                                    st.rerun()
                                else:
                                    next_qs = res_data.get("next_questions", [])
                                    st.session_state.current_questions = next_qs
                                    st.session_state.turn_count = res_data.get("turn", st.session_state.turn_count + 1)
                                    st.session_state.interview_messages.append({
                                        "sender": "historian",
                                        "text": "Every detail you share makes this memory more alive. Tell me:",
                                        "questions": next_qs
                                    })
                                    st.rerun()
                            else:
                                st.error("Could not process response.")
                        except Exception as e:
                            st.error(f"Error: {e}")

        with col_b2:
            if st.button("Finish & Weave Story ✨", use_container_width=True):
                st.session_state.interview_finished = True
                st.rerun()

    # ==============================================================================
    # PHASE 4: AGGREGATION & STORY WEAVING
    # ==============================================================================
    if st.session_state.interview_finished and not st.session_state.final_story:
        st.markdown("<br><hr style='border-top: 1px solid #d4af37;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Weaving Your Oral History</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-style: italic; color: #7a5c48;'>Gemini 1.5 Flash is transforming our conversation into a single, cohesive first-person narrative story...</p>", unsafe_allow_html=True)

        with st.spinner("Weaving sensory memories, ancestral traditions, and family voices..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/interview/finish",
                    json={"session_id": st.session_state.session_id},
                    timeout=30
                )
                if resp.status_code == 200:
                    fin_data = resp.json()
                    st.session_state.final_story = fin_data.get("story_narrative")
                    st.session_state.extracted_memory = fin_data.get("memory", {})
                    st.rerun()
                else:
                    st.error("Could not finalize memory story.")
            except Exception as e:
                st.error(f"Error finalizing: {e}")

    # Display the Synthesized Story
    if st.session_state.final_story:
        st.markdown("<br>", unsafe_allow_html=True)
        mem = st.session_state.extracted_memory or {}
        title = mem.get("title", "A Sacred Family Memory")
        era = mem.get("era", "Historic")
        loc = mem.get("location_name", "Ancestral Homeland")

        st.markdown(f"""
        <div class="memory-card" style="background: #fffaf0; border: 2px solid #d4af37; padding: 2.2rem;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <span class="vintage-title" style="font-size: 2rem;">{title}</span>
                <div class="date-tag" style="color: #8c6d1f; margin-top: 0.3rem;">{era} • {loc}</div>
            </div>
            <p style="font-size: 1.25rem; line-height: 1.85; color: #40291e; font-style: normal;">
                {st.session_state.final_story}
            </p>
            <div style="margin-top: 1.5rem; border-top: 1px dashed #e0d5c1; padding-top: 1rem; text-align: center;">
                <span class="gold-badge">✅ Preserved Forever in Family Heritage Vault</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c_end1, c_end2 = st.columns(2)
        with c_end1:
            if st.button("Start Another Interview 🎙️", use_container_width=True):
                st.session_state.session_id = None
                st.session_state.interview_messages = []
                st.session_state.current_questions = []
                st.session_state.turn_count = 1
                st.session_state.interview_finished = False
                st.session_state.final_story = None
                st.rerun()
        with c_end2:
            if st.button("View in Family Vault 📖", use_container_width=True):
                st.switch_page("app.py")
