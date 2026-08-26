"""
Visual Chronological Timeline Component for MemoryBox
Organizes memories by Year and Month into an interactive visual timeline.
"""

import streamlit as st
from typing import List, Callable
from collections import defaultdict
from ..utils.types import MemoryItemView


def render_chronological_timeline(memories: List[MemoryItemView], on_select_memory: Callable[[str], None]):
    """Renders memories grouped chronologically by year and month."""
    if not memories:
        st.info("No memories to display in timeline yet.")
        return

    # Group memories by Year descending, then Month
    grouped: dict[int, dict[str, list[MemoryItemView]]] = defaultdict(lambda: defaultdict(list))
    for mem in memories:
        yr = mem.year or 2026
        mo = mem.month or "January"
        grouped[yr][mo].append(mem)

    sorted_years = sorted(grouped.keys(), reverse=True)

    for year in sorted_years:
        st.markdown(f"""
        <div style="margin-top: 1.8rem; margin-bottom: 0.8rem; border-bottom: 2px solid #8b5a2b; padding-bottom: 4px;">
            <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 2rem; color: #8b5a2b; margin: 0;">
                📅 {year}
            </h2>
        </div>
        """, unsafe_allow_html=True)

        months_dict = grouped[year]
        # Month ordering if standard names, else alphabetical
        month_order = ["December", "November", "October", "September", "August", "July", "June", "May", "April", "March", "February", "January"]
        sorted_months = sorted(months_dict.keys(), key=lambda m: month_order.index(m) if m in month_order else 99)

        for month in sorted_months:
            st.markdown(f"""
            <div style="margin-left: 0.5rem; margin-top: 1rem; margin-bottom: 0.5rem;">
                <h4 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.15rem; color: #5c4232; font-weight: 700; margin: 0;">
                    📍 {month}
                </h4>
            </div>
            """, unsafe_allow_html=True)

            for mem in months_dict[month]:
                col_t1, col_t2 = st.columns([4, 1])
                with col_t1:
                    st.markdown(f"""
                    <div style="background: #ffffff; border-left: 3px solid #b8860b; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 700; color: #3b2a20; font-size: 1.05rem;">
                                {mem.title}
                            </span>
                            <span style="font-size: 0.8rem; background: #fdf8ee; color: #8b5a2b; padding: 2px 8px; border-radius: 10px; border: 1px solid #e7ded0;">
                                {mem.category}
                            </span>
                        </div>
                        <div style="color: #6b5344; font-size: 0.9rem; margin-top: 4px;">
                            "{mem.summary[:110]}..."
                        </div>
                        <div style="color: #9c8574; font-size: 0.8rem; margin-top: 4px;">
                            📍 {mem.location} &nbsp;·&nbsp; 🗓️ {mem.date}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_t2:
                    if st.button("Relive →", key=f"tl_btn_{mem.id}", use_container_width=True):
                        on_select_memory(mem.id)
