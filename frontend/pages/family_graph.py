"""
MemoryBox - Family Heritage Graph
Interactive network graph linking ancestors, sacred places, cultural rituals, and shared memories.
"""

import streamlit as st
import requests
import os
import json
import pandas as pd

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


def fetch_memories():
    headers = {}
    if st.session_state.get("auth_token"):
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    try:
        resp = requests.get(f"{BACKEND_URL}/api/memories/", headers=headers, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return data
    except Exception:
        pass

    # Default rich heritage memories so knowledge graph is always populated
    return [
        {
            "title": "Summer Mornings in the Mango Orchard",
            "location_name": "Mysore",
            "people_involved": ["Grandmother Lakshmi", "Uncle Raghavan", "Cousin Meena"],
            "cultural_traditions": ["Monsoon Tea Ritual", "Wood Carving"]
        },
        {
            "title": "The Golden Harvest & Sugarcane Fields",
            "location_name": "Thanjavur",
            "people_involved": ["Grandfather Sundaram", "Aunt Janaki", "Father"],
            "cultural_traditions": ["Thai Pongal Harvest Ceremony", "Clay Pot Blessing"]
        },
        {
            "title": "Temple Bells at Dawn by the River",
            "location_name": "Varanasi",
            "people_involved": ["Grandmother Lakshmi", "Great Aunt Savitri"],
            "cultural_traditions": ["Ganga Aarti", "Sanskrit Chanting"]
        }
    ]


memories = fetch_memories()

st.set_page_config(
    page_title="MemoryBox | Heritage Graph",
    page_icon="🕸️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Source+Serif+Pro:ital,wght@0,400;0,600&family=Courier+Prime:wght@700&display=swap');

.stApp {
    background: linear-gradient(180deg, #faf0e6 0%, #f5e6ca 100%);
    color: #5c4033;
    font-family: 'Source Serif Pro', Georgia, serif;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    font-style: italic;
    color: #5c4033 !important;
}

.graph-card {
    background: #fffaf0;
    border: 1px solid #e0d5c1;
    border-radius: 6px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 2px 4px 10px rgba(0,0,0,0.04);
}

.node-chip-person {
    background: #e6d5b8;
    color: #5c4033;
    padding: 0.35rem 0.8rem;
    border-radius: 16px;
    font-size: 0.95rem;
    display: inline-block;
    margin: 0.3rem;
    font-weight: 600;
}

.node-chip-place {
    background: #fff4d0;
    color: #8c6d1f;
    border: 1px solid #d4af37;
    padding: 0.35rem 0.8rem;
    border-radius: 16px;
    font-size: 0.95rem;
    display: inline-block;
    margin: 0.3rem;
}

.node-chip-tradition {
    background: #fde8e4;
    color: #a8071a;
    padding: 0.35rem 0.8rem;
    border-radius: 16px;
    font-size: 0.95rem;
    display: inline-block;
    margin: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown("<h1>Family Heritage Knowledge Graph</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-style: italic; color: #7a5c48;'>Discovered relationships weaving together generations, places, and sacred traditions.</p>", unsafe_allow_html=True)
with col_t2:
    if st.button("← Return to Vault", use_container_width=True):
        st.switch_page("app.py")

st.markdown("<hr style='border: none; border-top: 1px solid #d4af37; margin: 1rem 0 2rem 0;'>", unsafe_allow_html=True)


def fetch_memories():
    headers = {}
    if st.session_state.get("auth_token"):
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    try:
        resp = requests.get(f"{BACKEND_URL}/api/memories/", headers=headers, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []


memories = fetch_memories()

# Build Graph Nodes & Linkages
all_people = set()
all_places = set()
all_traditions = set()
connections = []

for m in memories:
    m_title = m.get("title", "Memory")
    people = m.get("people_involved", [])
    place = m.get("location_name")
    traditions = m.get("cultural_traditions", [])

    for p in people:
        p_clean = p.strip().title()
        if p_clean:
            all_people.add(p_clean)
            connections.append({"source": p_clean, "type": "Person", "memory": m_title})

    if place:
        pl_clean = place.strip().title()
        all_places.add(pl_clean)
        connections.append({"source": pl_clean, "type": "Place", "memory": m_title})

    for t in traditions:
        t_clean = t.strip().title()
        if t_clean:
            all_traditions.add(t_clean)
            connections.append({"source": t_clean, "type": "Tradition", "memory": m_title})

# Summary Metrics
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Stories", len(memories))
with c2:
    st.metric("Preserved Ancestors", len(all_people))
with c3:
    st.metric("Sacred Places", len(all_places))
with c4:
    st.metric("Cultural Traditions", len(all_traditions))

st.markdown("<br>", unsafe_allow_html=True)

# Visual Knowledge Representation
col_g1, col_g2 = st.columns([1, 2])

with col_g1:
    st.markdown("<h3>Graph Legend & Entities</h3>", unsafe_allow_html=True)
    st.markdown("<strong>👤 Preserved Family Members:</strong>", unsafe_allow_html=True)
    for p in sorted(list(all_people)):
        st.markdown(f"<span class='node-chip-person'>👤 {p}</span>", unsafe_allow_html=True)

    st.markdown("<br><strong>📍 Ancestral Places:</strong>", unsafe_allow_html=True)
    for pl in sorted(list(all_places)):
        st.markdown(f"<span class='node-chip-place'>📍 {pl}</span>", unsafe_allow_html=True)

    st.markdown("<br><strong>🪔 Sacred Traditions:</strong>", unsafe_allow_html=True)
    for tr in sorted(list(all_traditions)):
        st.markdown(f"<span class='node-chip-tradition'>🪔 {tr}</span>", unsafe_allow_html=True)

with col_g2:
    st.markdown("<h3>Relational Cross-Links</h3>", unsafe_allow_html=True)
    if connections:
        df_conn = pd.DataFrame(connections)
        # Group by Entity
        grouped = df_conn.groupby(["source", "type"])["memory"].apply(list).reset_index()
        for _, row in grouped.iterrows():
            badge_class = "node-chip-person" if row["type"] == "Person" else ("node-chip-place" if row["type"] == "Place" else "node-chip-tradition")
            icon = "👤" if row["type"] == "Person" else ("📍" if row["type"] == "Place" else "🪔")
            st.markdown(f"""
            <div class="graph-card">
                <span class="{badge_class}">{icon} {row['source']}</span>
                <span style="font-size: 0.85rem; color: #8c6d1f; margin-left: 0.5rem;">({row['type']})</span>
                <div style="margin-top: 0.8rem; font-size: 0.95rem;">
                    <strong>Connected Stories:</strong>
                    <ul style="margin-top: 0.3rem; margin-left: 1.2rem;">
                        {''.join([f'<li>{mem_name}</li>' for mem_name in row['memory']])}
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No connections discovered yet. Continue recording stories to grow your family knowledge graph!")
