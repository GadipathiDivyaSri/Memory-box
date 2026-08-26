"""
AI Understanding Service for MemoryBox
Orchestrates Gemini 1.5 Flash to understand, summarize, categorize, tag,
and reflect upon user memories with zero-crash heuristic fallbacks.
"""

import re
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("memorybox.ai_service")


class AIUnderstandingService:
    def __init__(self):
        self._gemini_configured = False
        self._model = None
        self._init_gemini()

    def _init_gemini(self):
        try:
            import os
            api_key = os.getenv("GOOGLE_API_KEY", "")
            if api_key:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
                self._gemini_configured = True
        except Exception as e:
            logger.info(f"Gemini client initializing with smart heuristic fallback: {e}")

    def understand_memory(
        self,
        raw_text: str,
        user_date: Optional[str] = None,
        user_location: Optional[str] = None,
        user_people: Optional[str] = None,
        user_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main AI understanding method.
        Analyzes the user's input and generates Title, Summary, Description,
        Smart Category, Tags, Inferred Location, People, Sentiment, and 'Why this matters'.
        """
        combined_text = f"{raw_text}\n{user_notes or ''}\nLocation hint: {user_location or ''}\nPeople hint: {user_people or ''}".strip()
        
        # 1. Attempt Gemini 1.5 Flash structured understanding
        if self._gemini_configured and self._model and len(combined_text) > 10:
            try:
                ai_result = self._gemini_extract(combined_text, user_date, user_location, user_people)
                if ai_result:
                    return ai_result
            except Exception as err:
                logger.warning(f"Live Gemini understanding exception: {err}. Using heuristic parser.")

        # 2. Resilient Smart Heuristic Fallback (Guaranteed to succeed)
        return self._heuristic_extract(raw_text, user_date, user_location, user_people, user_notes)

    def _gemini_extract(
        self,
        text: str,
        user_date: Optional[str],
        user_location: Optional[str],
        user_people: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        prompt = f"""
Analyze this personal memory and generate structured, meaningful metadata.
Input text:
\"\"\"{text}\"\"\"

Return ONLY a valid JSON object with EXACTLY these keys:
{{
  "title": "Poetic, warm 4-7 word title",
  "summary": "Concise 1-2 sentence overview of the moment",
  "description": "Clean, engaging paragraph summarizing the memory",
  "category": "One of: Family, Travel, College, Achievements, Events, Friends, Everyday, Work",
  "tags": ["3 to 5 relevant tags"],
  "year": 2025, // integer year deduced or mentioned, or current year
  "month": "Month name, e.g. March or October",
  "location": "City, place or landmark if mentioned, else 'Home'",
  "people": ["Names of people mentioned"],
  "sentiment": "e.g. Warm & Nostalgic, Triumphant, Serene",
  "why_it_matters": "A thoughtful 1-sentence reflection on why this moment is meaningful"
}}
"""
        response = self._model.generate_content(prompt)
        if response and response.text:
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            if "{" in cleaned and "}" in cleaned:
                start = cleaned.find("{")
                end = cleaned.rfind("}") + 1
                return json.loads(cleaned[start:end])
        return None

    def _heuristic_extract(
        self,
        raw_text: str,
        user_date: Optional[str],
        user_location: Optional[str],
        user_people: Optional[str],
        user_notes: Optional[str]
    ) -> Dict[str, Any]:
        """Fast, robust deterministic heuristic fallback."""
        clean = raw_text.strip()
        first_line = clean.split("\n")[0] if clean else "Cherished Family Memory"
        first_line = re.sub(r"[^\w\s]", "", first_line)
        words = first_line.split()
        title = " ".join(words[:6]).title() if len(words) >= 2 else "A Meaningful Memory"

        # Determine Category
        lower = clean.lower()
        if any(k in lower for k in ["temple", "mother", "father", "grandfather", "grandmother", "uncle", "aunt", "sister", "brother", "family"]):
            category = "Family"
        elif any(k in lower for k in ["trek", "trip", "travel", "flight", "train", "hotel", "hike", "beach", "hills", "mountain"]):
            category = "Travel"
        elif any(k in lower for k in ["college", "exam", "prof", "campus", "degree", "semester", "hostel", "study", "engineering"]):
            category = "College"
        elif any(k in lower for k in ["won", "award", "trophy", "hackathon", "first place", "promotion", "medal", "achievement"]):
            category = "Achievements"
        elif any(k in lower for k in ["wedding", "birthday", "festival", "sankranti", "diwali", "reception", "party", "ceremony"]):
            category = "Events"
        elif any(k in lower for k in ["friend", "buddy", "roommate", "gang"]):
            category = "Friends"
        elif any(k in lower for k in ["office", "work", "meeting", "client", "boss"]):
            category = "Work"
        else:
            category = "Everyday"

        # Deduce Year
        year_match = re.search(r"\b(19\d\d|20\d\d)\b", clean)
        year = int(year_match.group(1)) if year_match else (int(user_date[:4]) if user_date and len(user_date) >= 4 and user_date[:4].isdigit() else datetime.now().year)

        # Inferred People
        people = []
        if user_people:
            people = [p.strip() for p in user_people.split(",") if p.strip()]
        else:
            for kw in ["Grandfather", "Grandmother", "Mother", "Father", "Sister", "Brother", "Uncle", "Aunt"]:
                if kw.lower() in lower:
                    people.append(kw)

        # Inferred Tags
        tags = [category, str(year)]
        if people:
            tags.append(people[0])
        if "festival" in lower or "celebration" in lower:
            tags.append("Celebration")
        if "trip" in lower or "vacation" in lower:
            tags.append("Getaway")

        # Summary
        summary = (clean[:140] + "...") if len(clean) > 140 else clean
        if not summary:
            summary = "A special personal moment preserved in your memory box."

        # Why it matters
        why_it_matters = f"This moment captures the essence of {category.lower()} life, preserving details that might otherwise be forgotten with time."

        return {
            "title": title,
            "summary": summary,
            "description": clean,
            "category": category,
            "tags": list(dict.fromkeys(tags))[:5],
            "year": year,
            "month": datetime.now().strftime("%B"),
            "location": user_location.strip() if user_location else "Home",
            "people": people,
            "sentiment": "Reflective & Warm",
            "why_it_matters": why_it_matters
        }


# Singleton instance
ai_service = AIUnderstandingService()
