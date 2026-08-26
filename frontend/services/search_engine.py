"""
Smart Search & Natural Language Memory Retrieval Engine
Processes natural language questions and multi-facet filters to retrieve
relevant memories with AI-generated explanations of why they match.
"""

import re
from typing import List, Dict, Any, Optional
from ..utils.types import MemoryItemView


class MemorySearchEngine:
    """Intelligent semantic and keyword retrieval engine for MemoryBox."""

    def search(
        self,
        query: str,
        memories: List[MemoryItemView],
        category_filter: Optional[str] = None,
        year_filter: Optional[int] = None,
        tag_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes natural language query matching and multi-facet filtering.
        Returns:
            {
                "matches": [MemoryItemView, ...],
                "explanation": "AI generated explanation of why these memories matched...",
                "query": query,
                "total_found": int
            }
        """
        if not memories:
            return {
                "matches": [],
                "explanation": "No memories currently exist in your vault. Create a memory or explore demo memories to begin.",
                "query": query,
                "total_found": 0
            }

        candidates = list(memories)

        # 1. Apply Hard Category Filter
        if category_filter and category_filter.lower() != "all":
            candidates = [m for m in candidates if m.category.lower() == category_filter.lower()]

        # 2. Apply Year Filter
        if year_filter:
            candidates = [m for m in candidates if m.year == year_filter]

        # 3. Apply Tag Filter
        if tag_filter:
            candidates = [m for m in candidates if any(tag_filter.lower() in t.lower() for t in m.tags)]

        clean_q = (query or "").strip().lower()
        if not clean_q:
            return {
                "matches": candidates,
                "explanation": f"Displaying {len(candidates)} memories based on your selected filters.",
                "query": "",
                "total_found": len(candidates)
            }

        # 4. Natural Language Intent & Keyword Matching
        stopwords = {"show", "me", "my", "from", "the", "memories", "memory", "find", "what", "did", "take", "related", "containing", "about", "with", "in"}
        tokens = [t for t in re.split(r"\W+", clean_q) if len(t) > 2 and t not in stopwords]

        # Check for year in query (e.g. 2020, 2024, 2025, 2026, 1968, 1974)
        year_in_query = None
        yr_m = re.search(r"\b(19\d\d|20\d\d)\b", clean_q)
        if yr_m:
            year_in_query = int(yr_m.group(1))
        elif "last year" in clean_q:
            year_in_query = 2025
        elif "this year" in clean_q:
            year_in_query = 2026

        if year_in_query:
            candidates = [m for m in candidates if m.year == year_in_query]
            if not candidates:
                all_years = sorted(list({m.year for m in memories if m.year}))
                years_str = ", ".join(str(y) for y in all_years)
                return {
                    "matches": [],
                    "explanation": f"No memories found specifically from the year {year_in_query}. Your vault currently contains memories recorded in: {years_str}.",
                    "query": query,
                    "total_found": 0
                }

        # Check for month in query (e.g. January, August, October)
        months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        for m_name in months:
            if re.search(rf"\b{m_name}\b", clean_q):
                candidates = [m for m in candidates if m_name in m.date.lower() or m_name in m.summary.lower() or m_name in m.description.lower()]
                if not candidates:
                    return {
                        "matches": [],
                        "explanation": f"No memories found specifically for the month of {m_name.title()} in your vault.",
                        "query": query,
                        "total_found": 0
                    }
                break

        # Check for category hints
        category_hints = {
            "family": "Family",
            "relatives": "Family",
            "grandparents": "Family",
            "trip": "Travel",
            "trips": "Travel",
            "travel": "Travel",
            "vacation": "Travel",
            "college": "College",
            "university": "College",
            "school": "College",
            "won": "Achievements",
            "award": "Achievements",
            "trophy": "Achievements",
            "achievement": "Achievements",
            "birthday": "Events",
            "wedding": "Events",
            "festival": "Events",
            "party": "Events",
            "friends": "Friends",
            "friend": "Friends"
        }

        matched_category = None
        for hint_kw, cat_name in category_hints.items():
            if hint_kw in clean_q:
                matched_category = cat_name
                break

        scored: List[tuple[int, MemoryItemView, List[str]]] = []

        for mem in candidates:
            score = 0
            reasons = []

            # Exact or partial category match
            if matched_category and mem.category.lower() == matched_category.lower():
                score += 5
                reasons.append(f"categorized under {mem.category}")

            # Year match
            if year_in_query and mem.year == year_in_query:
                score += 5
                reasons.append(f"occurred in {mem.year}")

            # Keyword tokens match
            searchable_text = f"{mem.title} {mem.summary} {mem.description} {' '.join(mem.tags)} {mem.location} {' '.join(mem.people)}".lower()

            match_count = 0
            for t in tokens:
                if t in searchable_text:
                    match_count += 1
                    if t in mem.title.lower():
                        score += 3
                    elif any(t in tag.lower() for tag in mem.tags):
                        score += 3
                    elif any(t in p.lower() for p in mem.people):
                        score += 3
                        reasons.append(f"mentions {t.title()}")
                    else:
                        score += 1

            if match_count > 0:
                score += match_count * 2
                reasons.append(f"matches query terms ({match_count} terms)")

            # Emotional query match ("happiest", "nostalgic")
            if "happy" in clean_q or "joy" in clean_q:
                if "joy" in mem.sentiment.lower() or "ecstatic" in mem.sentiment.lower():
                    score += 4
                    reasons.append("has high joy sentiment")
            if "nostalgic" in clean_q or "ancestral" in clean_q or "heritage" in clean_q:
                if "nostalgic" in mem.sentiment.lower() or "heritage" in [t.lower() for t in mem.tags]:
                    score += 4
                    reasons.append("embodies deep nostalgic heritage")

            if score > 0:
                scored.append((score, mem, reasons))

        # Sort by relevance score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored]

        # Generate intelligent explanation
        if results:
            top_reasons = scored[0][2]
            reason_str = ", ".join(top_reasons) if top_reasons else "keyword relevance"
            explanation = (
                f"Found {len(results)} relevant {'memory' if len(results) == 1 else 'memories'} "
                f"matching '{query}'. The top match '{results[0].title}' was selected because it {reason_str}."
            )
        else:
            explanation = f"No memories directly matched '{query}'. Try searching for family members, places (like 'Mysore' or 'Thanjavur'), or years."

        return {
            "matches": results,
            "explanation": explanation,
            "query": query,
            "total_found": len(results)
        }


# Global search engine singleton
search_engine = MemorySearchEngine()
