"""
MemoryBox - Heritage Map
Interactive geographical exploration of family stories, ancestral migrations, and sacred places.
"""

import streamlit as st
import requests
import os
import pandas as pd
import pydeck as pdk

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
    page_title="MemoryBox | Heritage Map",
    page_icon="🗺️",
    layout="wide"
)

# Custom Vintage Styles
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

.memory-card {
    background: #fffaf0;
    border: 1px solid #e0d5c1;
    border-radius: 4px;
    padding: 1.2rem;
    margin-bottom: 1.2rem;
    box-shadow: 2px 4px 10px rgba(0,0,0,0.04);
    border-top: 3px solid #d4af37;
}
</style>
""", unsafe_allow_html=True)

col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown("<h1>Ancestral Heritage Map</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-style: italic; color: #7a5c48;'>Geographical landmarks and places where our family's stories unfolded.</p>", unsafe_allow_html=True)
with col_t2:
    if st.button("← Return to Vault", use_container_width=True):
        st.switch_page("app.py")

st.markdown("<hr style='border: none; border-top: 1px solid #d4af37; margin: 1rem 0 2rem 0;'>", unsafe_allow_html=True)


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

    # Default rich heritage memories so the map is always populated
    return [
        {
            "title": "Summer Mornings in the Mango Orchard",
            "era": "1960s",
            "year": "1968",
            "location_name": "Mysore, Karnataka",
            "latitude": 12.2958,
            "longitude": 76.6394,
            "story_narrative": "When I was 12, we walked 5km to school through the mango orchards. The morning air smelled of wet earth and raw green mangoes..."
        },
        {
            "title": "The Golden Harvest & Sugarcane Fields",
            "era": "1970s",
            "year": "1974",
            "location_name": "Thanjavur, Tamil Nadu",
            "latitude": 10.7870,
            "longitude": 79.1378,
            "story_narrative": "Every winter in Thanjavur, our village woke while the morning stars still shone bright. Grandfather Sundaram would lead us into the sugarcane fields..."
        },
        {
            "title": "Temple Bells at Dawn by the River",
            "era": "1950s",
            "year": "1955",
            "location_name": "Varanasi, Uttar Pradesh",
            "latitude": 25.3176,
            "longitude": 82.9739,
            "story_narrative": "The dawn boat ride along the sacred river with Grandmother Lakshmi chanting ancient hymns as clay lamps floated into the misty waters..."
        }
    ]


memories = fetch_memories()

# Default geo coordinates for Indian heritage sites if latitude/longitude not already present
geo_defaults = {
    "mysore": {"lat": 12.2958, "lon": 76.6394},
    "thanjavur": {"lat": 10.7870, "lon": 79.1378},
    "madras": {"lat": 13.0827, "lon": 80.2707},
    "chennai": {"lat": 13.0827, "lon": 80.2707},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "kolkata": {"lat": 22.5726, "lon": 88.3639},
    "varanasi": {"lat": 25.3176, "lon": 82.9739},
    "delhi": {"lat": 28.6139, "lon": 77.2090},
    "bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "bangalore": {"lat": 12.9716, "lon": 77.5946}
}

map_rows = []
for m in memories:
    lat = m.get("latitude")
    lon = m.get("longitude")
    loc = m.get("location_name", "Ancestral Homeland")

    if not lat or not lon:
        # Match from geo defaults
        loc_lower = str(loc).lower()
        for k, coords in geo_defaults.items():
            if k in loc_lower:
                lat = coords["lat"]
                lon = coords["lon"]
                break

    if not lat or not lon:
        lat = 13.0827
        lon = 80.2707

    map_rows.append({
        "title": m.get("title", "Oral Story"),
        "era": m.get("era", "1960s"),
        "year": m.get("year", "Historical"),
        "location": loc,
        "lat": float(lat),
        "lon": float(lon),
        "narrative": (m.get("story_narrative") or m.get("raw_transcript", ""))[:140] + "..."
    })

if map_rows:
    df_map = pd.DataFrame(map_rows)

    # PyDeck Map with warm vintage gold pin styling
    view_state = pdk.ViewState(
        latitude=df_map["lat"].mean(),
        longitude=df_map["lon"].mean(),
        zoom=5,
        pitch=25
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position=["lon", "lat"],
        get_color=[212, 175, 55, 200],  # Faded Gold #d4af37
        get_radius=40000,
        pickable=True,
        auto_highlight=True
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{title}\nEra: {era} ({year})\nLocation: {location}\n\n\"{narrative}\""},
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    st.pydeck_chart(r)

    st.markdown("<br><h3>Mapped Family Stories</h3>", unsafe_allow_html=True)
    c_m1, c_m2 = st.columns(2)
    for idx, row in enumerate(map_rows):
        col = c_m1 if idx % 2 == 0 else c_m2
        with col:
            st.markdown(f"""
            <div class="memory-card">
                <strong style="font-size: 1.2rem; color: #5c4033;">📍 {row['title']}</strong>
                <div style="color: #8c6d1f; font-family: 'Courier Prime', monospace; margin: 0.3rem 0;">
                    {row['era']} • {row['location']}
                </div>
                <p style="font-size: 0.95rem; color: #40291e;">{row['narrative']}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("No memories currently have geographical landmarks. Record a story mentioning a town or village!")
