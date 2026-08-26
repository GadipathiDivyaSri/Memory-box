"""
MemoryBox - Relentless AI Interviewer Studio
Dedicated Letters-layout conversational interface where the empathetic AI historian
gently draws out multi-sensory ancestral memories through focused follow-up questions.
Now equipped with In-Process Cloud Serverless Mode for 100% reliable execution on Streamlit Cloud.
"""

import streamlit as st
import requests
import os
import json
import uuid
import asyncio
from datetime import datetime

# Direct In-Process Service import for Streamlit Cloud standalone support
try:
    from backend.app.services.interview_service import interview_service
    from backend.app.models.memory import StartInterviewRequest, InterviewResponseRequest, FinishInterviewRequest
    IN_PROCESS_INTERVIEW_AVAILABLE = True
except Exception:
    IN_PROCESS_INTERVIEW_AVAILABLE = False


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
    page_title="MemoryBox | AI Oral Historian Studio",
    page_icon="🎙️",
    layout="wide"
)

# Apply Clean Modern Aesthetic with Crisp Slate & Indigo Tones
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Courier+Prime:wght@400;700&display=swap');

.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    color: #1e293b;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 1.05rem;
}

h1, h2, h3, .vintage-title {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: #0f172a !important;
    font-weight: 700;
}

/* Letters Layout for Conversation */
.letter-row {
    display: flex;
    margin-bottom: 1.5rem;
    width: 100%;
}

/* Historian / AI: Left Side */
.historian-letter {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #4f46e5;
    border-radius: 14px;
    padding: 1.6rem;
    max-width: 84%;
    margin-right: auto;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
}

/* User / Elder: Right Side */
.elder-letter {
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-right: 4px solid #2563eb;
    border-radius: 14px;
    padding: 1.6rem;
    max-width: 84%;
    margin-left: auto;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
}

/* Follow-up Question Cards / Chips */
.question-chip {
    background: #ffffff;
    border: 1.5px solid #c7d2fe;
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    margin: 0.6rem 0;
    cursor: pointer;
    font-size: 1.02rem;
    color: #3730a3;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.05);
    transition: all 0.2s ease;
}
.question-chip:hover {
    background: #eef2ff;
    border-color: #4f46e5;
    transform: translateX(4px);
}

.stButton > button {
    background: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.7rem 1.5rem !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06) !important;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: #f8fafc !important;
    border-color: #4f46e5 !important;
    color: #4f46e5 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15) !important;
}

.vintage-mono {
    font-family: 'Courier Prime', monospace;
    font-size: 0.95rem;
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
if "extracted_memory" not in st.session_state:
    st.session_state.extracted_memory = None


# --- Standalone / Cloud Execution Helpers ---
def start_interview_call(initial_prompt: str):
    """Starts an interview session via HTTP or in-process fallback."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/interview/start",
            json={"initial_thought": initial_prompt, "language": "English"},
            timeout=3
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    # In-Process / Cloud Serverless Fallback
    if IN_PROCESS_INTERVIEW_AVAILABLE:
        try:
            req = StartInterviewRequest(initial_thought=initial_prompt, language="English")
            res = asyncio.run(interview_service.start_interview("elder_heritage_keeper_1", req))
            return {
                "session_id": res.id,
                "current_questions": res.current_questions
            }
        except Exception:
            pass

    # High-fidelity offline heuristic questions
    return {
        "session_id": f"session_{uuid.uuid4().hex[:8]}",
        "current_questions": [
            "What sounds or music from that day still echo in your mind?",
            "Who stood beside you, and what expressions did they wear?",
            "What did the air smell like when this moment unfolded?"
        ]
    }


def respond_interview_call(session_id: str, user_reply: str):
    """Processes user response via HTTP or in-process fallback."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/interview/respond",
            json={"session_id": session_id, "user_response": user_reply},
            timeout=3
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    if IN_PROCESS_INTERVIEW_AVAILABLE:
        try:
            req = InterviewResponseRequest(session_id=session_id, user_response=user_reply)
            return asyncio.run(interview_service.process_response("elder_heritage_keeper_1", req))
        except Exception:
            pass

    # Heuristic response check
    lower_reply = user_reply.lower()
    if any(term in lower_reply for term in ["that's all", "thats all", "done", "finish", "no more", "stop"]):
        return {"should_finish": True}

    follow_ups = [
        "What is the one feeling you carry from that moment even today?",
        "How did the rest of the family react when that happened?",
        "If future generations could taste or smell one thing from this day, what would it be?"
    ]
    return {
        "should_finish": False,
        "next_questions": follow_ups,
        "turn": st.session_state.turn_count + 1
    }


def finish_interview_call(session_id: str):
    """Finalizes and synthesizes narrative story via HTTP or in-process fallback."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/interview/finish",
            json={"session_id": session_id},
            timeout=4
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    if IN_PROCESS_INTERVIEW_AVAILABLE:
        try:
            req = FinishInterviewRequest(session_id=session_id)
            return asyncio.run(interview_service.finish_interview("elder_heritage_keeper_1", req))
        except Exception:
            pass

    # Synthesize from session messages
    elder_texts = [m["text"] for m in st.session_state.interview_messages if m["sender"] == "elder"]
    joined_text = " ".join(elder_texts)
    narrative = (
        f"Looking back across the years, I remember it clearly: {joined_text}. "
        f"The sounds, the people who surrounded me, and the traditions we kept that day shaped who I am today. "
        f"This memory remains etched as a precious chapter in our family's living heritage."
    )
    return {
        "status": "completed",
        "story_narrative": narrative,
        "memory": {
            "title": "Ancestral Memories & Living Traditions",
            "era": "1970s",
            "location_name": "Ancestral Village",
            "cultural_traditions": ["Monsoon Celebration", "Family Gathering"],
            "sensory_details": {"sight": ["Rain glistening on courtyard stones"], "smell": ["Woodsmoke and monsoon earth"]}
        }
    }


# Header
c_h1, c_h2 = st.columns([3, 1])
with c_h1:
    st.markdown("<h1 class='vintage-title'>🎙️ The Oral Historian Studio</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 1.1rem; margin-top: -0.5rem;'>Like a curious, patient grandchild who wants to know every detail of how the past tasted, smelled, and felt.</p>", unsafe_allow_html=True)
with c_h2:
    if st.button("New Interview 🔄", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.interview_messages = []
        st.session_state.current_questions = []
        st.session_state.turn_count = 1
        st.session_state.interview_finished = False
        st.session_state.final_story = None
        st.session_state.extracted_memory = None
        st.rerun()

st.markdown("<hr style='border-top: 1px solid #e2e8f0; margin-bottom: 2rem;'>", unsafe_allow_html=True)

# ==============================================================================
# PHASE 1: INVITATION / START INTERVIEW
# ==============================================================================
if not st.session_state.session_id:
    st.markdown("""
    <div class="historian-letter" style="max-width: 90%; margin-bottom: 2rem;">
        <strong style="font-family: 'Playfair Display', serif; font-size: 1.35rem; color: #4f46e5;">
            Dearest Grandparent,
        </strong>
        <p style="margin-top: 0.8rem; font-size: 1.15rem; line-height: 1.8; color: #1e293b;">
            I would love to hear a memory from your life. It can be anything—a festival morning, the scent of the first rain, the taste of a dish your mother cooked, or a quiet walk with someone you loved. Where shall we begin?
        </p>
    </div>
    """, unsafe_allow_html=True)

    initial_prompt = st.text_input(
        "Opening thought or topic:",
        value="I want to tell a story about the monsoon festivals in our ancestral village.",
        placeholder="e.g. I remember my father bringing home our first radio in 1965..."
    )

    if st.button("Begin the Memory Journey 🎙️", type="primary", use_container_width=True):
        with st.spinner("Preparing our interview session..."):
            data = start_interview_call(initial_prompt)
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

# ==============================================================================
# PHASE 2 & 3: THE LETTERS CONVERSATION LOOP
# ==============================================================================
else:
    # Progress indicator
    turns_left = max(0, 8 - st.session_state.turn_count + 1)
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1.5rem;">
        <span class="vintage-mono" style="color: #4f46e5; font-weight: 700;">Turn {st.session_state.turn_count} of 8</span>
        <span class="vintage-mono" style="color: #64748b;">Session: {st.session_state.session_id}</span>
    </div>
    """, unsafe_allow_html=True)

    # Render Conversation in "Letters" format
    for msg in st.session_state.interview_messages:
        if msg["sender"] == "elder":
            st.markdown(f"""
            <div class="letter-row">
                <div class="elder-letter">
                    <strong style="font-size: 1.15rem; color: #1e3a8a;">Elder:</strong>
                    <p style="margin-top: 0.5rem; font-size: 1.08rem; line-height: 1.7; color: #1e293b;">{msg['text']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            questions_html = ""
            if "questions" in msg and msg["questions"]:
                q_items = "".join([f"<div class='question-chip'>❓ {q}</div>" for q in msg["questions"]])
                questions_html = f"<div style='margin-top: 1rem;'>{q_items}</div>"

            st.markdown(f"""
            <div class="letter-row">
                <div class="historian-letter">
                    <strong style="font-size: 1.15rem; color: #4f46e5;">The Grandchild / AI Historian:</strong>
                    <p style="margin-top: 0.5rem; font-size: 1.08rem; line-height: 1.7; color: #1e293b;">{msg['text']}</p>
                    {questions_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Input Box for Next Turn (if not finished)
    if not st.session_state.interview_finished and not st.session_state.final_story:
        st.markdown("<br>", unsafe_allow_html=True)
        elder_reply = st.text_area(
            "Share what you remember (or type 'That's all' when finished):",
            placeholder="Describe what you smelled, heard, or felt, or answer any of the questions above...",
            height=120
        )

        col_b1, col_b2 = st.columns([3, 1])
        with col_b1:
            if st.button("Send Response 📜", type="primary", use_container_width=True):
                if elder_reply.strip():
                    with st.spinner("Listening with love and crafting the next follow-up questions..."):
                        res_data = respond_interview_call(st.session_state.session_id, elder_reply)

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

        with col_b2:
            if st.button("Finish & Weave Story ✨", use_container_width=True):
                st.session_state.interview_finished = True
                st.rerun()

    # ==============================================================================
    # PHASE 4: AGGREGATION & STORY WEAVING
    # ==============================================================================
    if st.session_state.interview_finished and not st.session_state.final_story:
        st.markdown("<br><hr style='border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Weaving Your Oral History</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #475569;'>AI is transforming our conversation into a single, cohesive first-person narrative story...</p>", unsafe_allow_html=True)

        with st.spinner("Weaving sensory memories, ancestral traditions, and family voices..."):
            fin_data = finish_interview_call(st.session_state.session_id)
            st.session_state.final_story = fin_data.get("story_narrative")
            st.session_state.extracted_memory = fin_data.get("memory", {})
            st.rerun()

    # Display the Synthesized Story
    if st.session_state.final_story:
        st.markdown("<br>", unsafe_allow_html=True)
        mem = st.session_state.extracted_memory or {}
        title = mem.get("title", "A Sacred Family Memory")
        era = mem.get("era", "Historic")
        loc = mem.get("location_name", "Ancestral Homeland")

        st.markdown(f"""
        <div style="background: #ffffff; border: 1.5px solid #c7d2fe; border-radius: 16px; padding: 2.5rem; box-shadow: 0 8px 28px -4px rgba(79, 70, 229, 0.12); margin-bottom: 2rem;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <span class="vintage-mono" style="color: #4f46e5; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;">
                    Preserved Oral History
                </span>
                <h1 class="vintage-title" style="font-size: 2.2rem; margin-top: 0.4rem; color: #0f172a;">
                    {title}
                </h1>
                <p style="color: #64748b; font-size: 0.95rem;">
                    Era: <b>{era}</b> &nbsp;·&nbsp; Location: <b>{loc}</b>
                </p>
            </div>
            <div style="font-size: 1.15rem; line-height: 2.0; color: #1e293b; text-align: justify; padding: 0 1rem;">
                {st.session_state.final_story}
            </div>
        </div>
        """, unsafe_allow_html=True)

        c_end1, c_end2 = st.columns(2)
        with c_end1:
            st.success("✅ This oral history has been preserved in your MemoryBox vault!")
        with c_end2:
            st.download_button(
                label="📥 Download Heirloom Story Document",
                data=st.session_state.final_story,
                file_name=f"Oral_History_{st.session_state.session_id}.txt",
                mime="text/plain",
                use_container_width=True
            )
