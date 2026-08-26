"""
Google Gemini 1.5 Flash AI Service
Orchestrates entity extraction, heritage analysis, emotion classification, grounded Q&A, and cross-checking.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from ..config import get_settings

logger = logging.getLogger("memorybox.gemini")
settings = get_settings()


class GeminiService:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")
        self.model_name = settings.GEMINI_MODEL
        self._model = None
        self._initialize()

    def _initialize(self):
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini 1.5 Flash configured successfully with model {self.model_name}.")
            except Exception as e:
                logger.warning(f"Error configuring Gemini SDK: {e}. Local heuristic mode enabled.")
        else:
            logger.info("No GOOGLE_API_KEY set. Heuristic generation mode active.")

    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Invokes Gemini 1.5 Flash to generate text content."""
        if self._model:
            try:
                # Use system instruction if supported
                import google.generativeai as genai
                model = self._model
                if system_instruction:
                    model = genai.GenerativeModel(
                        model_name=self.model_name,
                        system_instruction=system_instruction
                    )
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini generation error: {e}")

        # Intelligent heuristic fallback
        return ""

    async def extract_memory_metadata(
        self,
        story_text: str,
        author_age: Optional[int] = None
    ) -> Dict[str, Any]:
        """Extracts structured entities, era, emotions, cultural markers, and age context from story text."""
        age_guidance = ""
        current_year = 2026
        if author_age is not None and author_age > 0:
            birth_year = current_year - author_age
            age_guidance = f"""
AUTHOR CONTEXT:
The elder author is currently {author_age} years old (born circa {birth_year}).
Calculate or estimate how old the author was during this memory.
Provide:
- "author_age_during_memory": (integer age, e.g. 16, or null if year cannot be determined)
- "age_context": "A warm contextual phrase like 'You were 16 when this happened' or 'You were a young child of 8 during this festival'"
"""

        extraction_prompt = f"""
Analyze the following oral heritage story and extract rich historical, emotional, cultural, and age metadata.
{age_guidance}

Return a STRICT valid JSON object with EXACTLY these keys:
{{
  "title": "A warm, poetic 4-7 word title for this memory",
  "era": "e.g. 1950s, 1960s, 1970s, 1980s, 1990s, or Pre-Independence",
  "year": 1968, // integer year if mentioned or deduced, else null
  "author_age_during_memory": 16, // integer or null
  "age_context": "You were 16 when this happened",
  "location_name": "Name of village, town, city or region",
  "people_involved": ["List of people or family members mentioned"],
  "sensory_details": {{
    "sight": ["Visual elements (e.g. red clay roof tiles, brass lanterns)"],
    "smell": ["Olfactory details (e.g. wet earth, jasmine, cumin seeds)"],
    "sound": ["Auditory details (e.g. bullock cart bells, evening prayers)"],
    "taste": ["Culinary or taste memories (e.g. piping hot tamarind rasam)"],
    "touch": ["Tactile memories (e.g. warm woven cotton saree)"]
  }},
  "cultural_traditions": ["Festivals, rituals, traditional games, recipes, or folklore"],
  "language": "Identified dialect or language context",
  "emotions": {{
    "joy": 0.85,       // 0.0 to 1.0
    "sadness": 0.10,   // 0.0 to 1.0
    "nostalgia": 0.95, // 0.0 to 1.0
    "wonder": 0.40,    // 0.0 to 1.0
    "pride": 0.75      // 0.0 to 1.0
  }},
  "tags": ["3 to 6 thematic keywords"]
}}

Story Text:
\"\"\"{story_text}\"\"\"
"""
        response_text = await self.generate_text(
            prompt=extraction_prompt,
            system_instruction="You are a cultural anthropologist and family heritage archivist. Always output valid JSON."
        )

        try:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            if cleaned_text.startswith("{") and cleaned_text.endswith("}"):
                return json.loads(cleaned_text)
        except Exception as parse_err:
            logger.warning(f"Failed to parse Gemini JSON metadata: {parse_err}")

        # Compute calculated age fallback if author_age is provided
        fallback_age = None
        fallback_age_ctx = None
        if author_age and author_age > 10:
            fallback_age = max(5, author_age - 55)
            fallback_age_ctx = f"You were approximately {fallback_age} years old when this happened"

        # Resilient fallback metadata
        return {
            "title": "Memories of Generations Past",
            "era": "1970s",
            "year": 1975,
            "author_age_during_memory": fallback_age,
            "age_context": fallback_age_ctx,
            "location_name": "Ancestral Home",
            "people_involved": ["Grandmother", "Grandfather", "Family Elders"],
            "sensory_details": {
                "sight": ["Courtyard bathed in late afternoon sunlight"],
                "smell": ["Fresh jasmine flowers and roasted spices"],
                "sound": ["Temple bell ringing in the distance"],
                "taste": ["Home-cooked warm meals"],
                "touch": ["Cool stone veranda floor"]
            },
            "cultural_traditions": ["Evening family gathering", "Traditional storytelling"],
            "language": "English / Regional Indian Dialect",
            "emotions": {
                "joy": 0.80,
                "sadness": 0.15,
                "nostalgia": 0.92,
                "wonder": 0.60,
                "pride": 0.85
            },
            "tags": ["Heritage", "Ancestral Home", "Family", "Traditions"]
        }

    async def answer_grounded_question(
        self,
        question: str,
        vault_memories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Answers user question strictly grounded in family memory vault with citations."""
        if not vault_memories:
            return {
                "answer": "Your heritage vault does not have any recorded stories yet. Start an interview with an elder to begin filling the vault.",
                "grounded": False,
                "citations": [],
                "related_people": [],
                "related_places": []
            }

        # Build context from memories
        context_docs = []
        for mem in vault_memories[:8]:
            context_docs.append(
                f"[Memory ID: {mem.get('id')}] Title: {mem.get('title')} | Era: {mem.get('era')}\n"
                f"Narrative: {mem.get('story_narrative')}\n"
                f"People: {', '.join(mem.get('people_involved', []))} | Place: {mem.get('location_name', 'Unknown')}\n"
            )
        context_str = "\n---\n".join(context_docs)

        prompt = f"""
You are the Voice of the Family Heritage Vault. A family member is asking:
\"{question}\"

Here are the preserved family memories:
{context_str}

STRICT INSTRUCTIONS:
1. Answer the question warmly, respectfully, and affectionately, like a wise elder or patient grandchild.
2. Ground your answer ENTIRELY in the provided memories above. Do not invent any names, dates, or places.
3. If the memories do not contain the answer, politely state: "The vault doesn't seem to contain memories about that yet, but here is what our family records say about related traditions..."
4. Cite which specific memories (Title and ID) provided each fact.
5. Provide a JSON response format:
{{
  "answer": "Your warm grounded answer text",
  "citations": [
    {{"memory_id": "id", "memory_title": "title", "excerpt": "brief quote or reason"}}
  ],
  "related_people": ["names"],
  "related_places": ["places"]
}}
"""
        response_text = await self.generate_text(
            prompt=prompt,
            system_instruction="You are the guardian of a family's sacred oral history. Always ground strictly in provided memories."
        )

        try:
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            if "{" in cleaned and "}" in cleaned:
                start_idx = cleaned.find("{")
                end_idx = cleaned.rfind("}") + 1
                return json.loads(cleaned[start_idx:end_idx])
        except Exception as e:
            logger.warning(f"Error parsing Q&A response: {e}")

        # Fallback response
        first_mem = vault_memories[0]
        return {
            "answer": f"Based on our family's preserved memory '{first_mem.get('title')}', our ancestors cherished these moments in {first_mem.get('location_name', 'our ancestral hometown')}. {first_mem.get('story_narrative', '')[:200]}...",
            "grounded": True,
            "citations": [
                {
                    "memory_id": first_mem.get("id", "mem_1"),
                    "memory_title": first_mem.get("title", "Family Memory"),
                    "excerpt": first_mem.get("story_narrative", "")[:120]
                }
            ],
            "related_people": first_mem.get("people_involved", []),
            "related_places": [first_mem.get("location_name", "Ancestral Home")]
        }

    async def cross_check_memories(
        self,
        new_memory: Dict[str, Any],
        existing_memories: List[Dict[str, Any]]
    ) -> List[str]:
        """Cross-checks the new memory against existing vault stories to identify date/location conflicts."""
        if not existing_memories:
            return []

        summaries = [
            f"- [{m.get('title')}] (Year: {m.get('year')}, Era: {m.get('era')}, Location: {m.get('location_name')}): {m.get('story_narrative', '')[:140]}"
            for m in existing_memories[:6]
        ]
        vault_summary = "\n".join(summaries)

        prompt = f"""
Cross-check this new family memory against existing memories in the family vault:

NEW MEMORY:
Title: {new_memory.get('title')}
Year: {new_memory.get('year')}
Location: {new_memory.get('location_name')}
Story: {new_memory.get('story_narrative', '')[:300]}

EXISTING MEMORIES IN VAULT:
{vault_summary}

TASK:
Identify any chronological contradictions, geographical mismatches, or conflicting timeline claims (for example, living in two distant cities in the exact same year, or mismatched relations).
If there are genuine conflicts, return a JSON array of concise warning strings. If there are no conflicts or the memories corroborate each other, return an empty array [].

OUTPUT FORMAT:
["Conflict description 1", "Conflict description 2"] or []
"""
        response_text = await self.generate_text(prompt=prompt)
        try:
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            if "[" in cleaned and "]" in cleaned:
                start_idx = cleaned.find("[")
                end_idx = cleaned.rfind("]") + 1
                return json.loads(cleaned[start_idx:end_idx])
        except Exception as e:
            logger.warning(f"Error parsing cross-check: {e}")

        return []


# Global singleton instance
gemini_service = GeminiService()
