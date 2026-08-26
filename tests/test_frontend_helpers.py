"""
Unit Tests for Frontend Services and Helper Logic
Tests:
- AI understanding extraction and smart heuristic fallback
- Natural language memory search and query explanations
- Category filtering and timeline grouping
- Demo data completeness and types
"""

import pytest
from frontend.utils.types import MemoryItemView, SMART_CATEGORIES
from frontend.services.demo_data import get_demo_memories
from frontend.services.ai_service import ai_service
from frontend.services.search_engine import search_engine
from frontend.services.api_client import calculate_vault_stats


def test_demo_data_integrity():
    """Verifies that the demo dataset contains realistic memories across all key categories."""
    mems = get_demo_memories()
    assert len(mems) >= 5

    categories = {m.category for m in mems}
    assert "Family" in categories
    assert "Travel" in categories
    assert "College" in categories
    assert "Achievements" in categories
    assert "Events" in categories

    for m in mems:
        assert m.title
        assert m.summary
        assert m.year > 2000
        assert m.why_it_matters is not None
        assert m.is_demo is True


def test_ai_understanding_heuristic():
    """Tests the resilient heuristic memory understanding pipeline."""
    sample_text = "We celebrated Diwali at our grandmother's house in Mysore in 2024. The whole family made sweet laddoos."
    result = ai_service.understand_memory(raw_text=sample_text)

    assert result["title"]
    assert result["summary"]
    assert result["category"] in ("Family", "Events")
    assert result["year"] == 2024
    assert "Grandmother" in result["people"] or "Family" in result["tags"]
    assert len(result["tags"]) > 0
    assert result["why_it_matters"]


def test_natural_language_search_engine():
    """Tests natural language retrieval of memories with AI explanations."""
    mems = get_demo_memories()

    # Query 1: Family
    res_fam = search_engine.search("Show my family memories", mems)
    assert res_fam["total_found"] > 0
    assert any(m.category == "Family" for m in res_fam["matches"])
    assert "explanation" in res_fam

    # Query 2: Trips
    res_travel = search_engine.search("What trips did I take?", mems)
    assert res_travel["total_found"] > 0
    assert any(m.category == "Travel" for m in res_travel["matches"])

    # Query 3: College
    res_college = search_engine.search("Find memories related to college", mems)
    assert res_college["total_found"] > 0
    assert any(m.category == "College" for m in res_college["matches"])

    # Query 4: Year 2025
    res_yr = search_engine.search("Memories from 2025", mems)
    assert res_yr["total_found"] > 0
    assert all(m.year == 2025 for m in res_yr["matches"])


def test_smart_categories_list():
    """Verifies defined categories."""
    assert len(SMART_CATEGORIES) >= 8
    cat_names = [c["name"] for c in SMART_CATEGORIES]
    assert "All" in cat_names
    assert "Family" in cat_names
    assert "Travel" in cat_names


def test_navbar_tabs_structure():
    """Verifies navbar renders all 6 tabs without TypeError."""
    from frontend.components.navbar import render_navbar
    from unittest.mock import MagicMock, patch

    mock_st = MagicMock()
    mock_cols = [MagicMock() for _ in range(6)]
    mock_st.columns.return_value = mock_cols

    with patch("frontend.components.navbar.st", mock_st):
        render_navbar(active_tab="home", on_tab_change=lambda x: None)

    assert mock_st.columns.called
    assert mock_st.button.call_count == 6

