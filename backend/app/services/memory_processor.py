"""
Memory Processor Service
Pipeline for extracting historical context, cross-checking conflicts, calculating
digital archive health scores, and charting decade-by-decade emotional trajectories.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..models.memory import (
    MemoryItem,
    SensoryDetails,
    EmotionScores,
    DigitalHealthScoreResponse
)
from ..database.firestore_client import db_client
from .gemini_service import gemini_service

logger = logging.getLogger("memorybox.processor")


class MemoryProcessor:
    async def process_and_save_memory(
        self,
        user_id: str,
        title: str,
        raw_transcript: str,
        story_narrative: str,
        language: str = "English",
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Runs the complete memory extraction, cross-checking, and persistence pipeline."""
        memory_id = f"mem_{uuid.uuid4().hex[:12]}"
        media_urls = media_urls or []

        # Step 1: AI Metadata Extraction via Gemini 1.5 Flash with Author Age Context
        user = await db_client.get_user(user_id)
        author_age = user.get("age", 78) if user else 78
        extracted = await gemini_service.extract_memory_metadata(story_narrative, author_age=author_age)

        final_title = title if (title and title != "Family Heritage Story" and title != "A Life Remembered") else extracted.get("title", title)
        era = extracted.get("era", "1970s")
        year = extracted.get("year")
        author_age_during_memory = extracted.get("author_age_during_memory")
        age_context = extracted.get("age_context")
        location_name = extracted.get("location_name")
        people_involved = extracted.get("people_involved", [])
        cultural_traditions = extracted.get("cultural_traditions", [])
        tags = list(set(extracted.get("tags", []) + [era]))

        # Format sensory details
        raw_sensory = extracted.get("sensory_details", {})
        sensory = SensoryDetails(
            sight=raw_sensory.get("sight", []),
            smell=raw_sensory.get("smell", []),
            sound=raw_sensory.get("sound", []),
            taste=raw_sensory.get("taste", []),
            touch=raw_sensory.get("touch", [])
        )

        # Format emotion scores
        raw_emotions = extracted.get("emotions", {})
        emotions = EmotionScores(
            joy=float(raw_emotions.get("joy", 0.8)),
            sadness=float(raw_emotions.get("sadness", 0.15)),
            nostalgia=float(raw_emotions.get("nostalgia", 0.9)),
            wonder=float(raw_emotions.get("wonder", 0.5)),
            pride=float(raw_emotions.get("pride", 0.8))
        )

        # Step 2: Memory Cross-Check against existing vault
        existing_memories = await db_client.list_memories(user_id=user_id, limit=20)
        candidate_dict = {
            "title": final_title,
            "year": year,
            "era": era,
            "location_name": location_name,
            "story_narrative": story_narrative
        }
        conflicts = await gemini_service.cross_check_memories(candidate_dict, existing_memories)

        # Step 3: Build MemoryItem with Age Contextualization
        memory_item = MemoryItem(
            id=memory_id,
            user_id=user_id,
            title=final_title,
            raw_transcript=raw_transcript,
            story_narrative=story_narrative,
            era=era,
            year=year,
            author_age_during_memory=author_age_during_memory,
            age_context=age_context,
            location_name=location_name,
            people_involved=people_involved,
            sensory_details=sensory,
            cultural_traditions=cultural_traditions,
            language=language,
            emotions=emotions,
            tags=tags,
            media_urls=media_urls,
            conflicts_detected=conflicts,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Step 4: Persist to Firestore
        await db_client.save_memory(memory_item.model_dump())
        await db_client.log_audit_event(
            user_id=user_id,
            action="memory.created",
            resource_id=memory_id,
            metadata={"title": final_title, "era": era, "conflicts": len(conflicts)}
        )

        return memory_item.model_dump()

    async def calculate_health_score(self, user_id: str) -> DigitalHealthScoreResponse:
        """Calculates archive completeness percentage and heritage preservation milestones."""
        memories = await db_client.list_memories(user_id=user_id, limit=200)
        total_count = len(memories)

        if total_count == 0:
            return DigitalHealthScoreResponse(
                completion_percentage=10,
                total_memories=0,
                eras_covered=[],
                people_preserved=0,
                places_mapped=0,
                traditions_documented=0,
                status_summary="Vault created. Awaiting the first recorded memory."
            )

        eras = set()
        people = set()
        places = set()
        traditions = set()

        for m in memories:
            if m.get("era"):
                eras.add(m.get("era"))
            for p in m.get("people_involved", []):
                people.add(p.strip())
            if m.get("location_name"):
                places.add(m.get("location_name").strip())
            for t in m.get("cultural_traditions", []):
                traditions.add(t.strip())

        # Scoring heuristics based on diversity of coverage:
        # Base: min(total_count * 8, 40)
        # Eras: min(len(eras) * 10, 20)
        # People: min(len(people) * 5, 20)
        # Traditions: min(len(traditions) * 5, 20)
        score = min(
            100,
            int(min(total_count * 8, 40) + min(len(eras) * 10, 20) + min(len(people) * 5, 20) + min(len(traditions) * 5, 20))
        )
        # Guarantee minimum 25% if memories exist
        score = max(score, 25)

        # Determine family generations based on user age
        user = await db_client.get_user(user_id)
        user_age = user.get("age", 78) if user else 78
        if user_age >= 70:
            generations = 4
        elif user_age >= 45:
            generations = 3
        elif user_age >= 25:
            generations = 2
        else:
            generations = 1

        summary = f"Your Archive is {score}% Complete • Our family spans {generations} generations (Elder age: {user_age})"

        return DigitalHealthScoreResponse(
            completion_percentage=score,
            total_memories=total_count,
            eras_covered=sorted(list(eras)),
            people_preserved=len(people),
            places_mapped=len(places),
            traditions_documented=len(traditions),
            status_summary=summary
        )

    async def get_emotion_timeline(self, user_id: str) -> List[Dict[str, Any]]:
        """Calculates average Joy, Nostalgia, and Sadness indexed across historical decades."""
        memories = await db_client.list_memories(user_id=user_id, limit=200)

        # Standard chronological eras
        standard_eras = ["1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s"]
        era_stats: Dict[str, Dict[str, Any]] = {
            era: {"joy": [], "nostalgia": [], "sadness": [], "count": 0}
            for era in standard_eras
        }

        for m in memories:
            era = m.get("era", "")
            matched_era = None
            for se in standard_eras:
                if se in era:
                    matched_era = se
                    break

            if not matched_era:
                # Deduce from year if present
                yr = m.get("year")
                if yr:
                    dec = f"{(yr // 10) * 10}s"
                    if dec in era_stats:
                        matched_era = dec

            if matched_era and m.get("emotions"):
                em = m["emotions"]
                era_stats[matched_era]["joy"].append(em.get("joy", 0.7))
                era_stats[matched_era]["nostalgia"].append(em.get("nostalgia", 0.8))
                era_stats[matched_era]["sadness"].append(em.get("sadness", 0.2))
                era_stats[matched_era]["count"] += 1

        timeline = []
        for era in standard_eras:
            data = era_stats[era]
            count = data["count"]
            if count > 0:
                timeline.append({
                    "era": era,
                    "joy": round(sum(data["joy"]) / count, 2),
                    "nostalgia": round(sum(data["nostalgia"]) / count, 2),
                    "sadness": round(sum(data["sadness"]) / count, 2),
                    "stories_count": count
                })
            else:
                # Default smooth trajectory for aesthetic continuity
                timeline.append({
                    "era": era,
                    "joy": 0.65,
                    "nostalgia": 0.80,
                    "sadness": 0.20,
                    "stories_count": 0
                })

        return timeline

    async def get_memory_connections(self, user_id: str) -> Dict[str, Any]:
        """Extracts network of relationships connecting memories through shared family members and places."""
        memories = await db_client.list_memories(user_id=user_id, limit=100)
        people_map: Dict[str, List[str]] = {}
        places_map: Dict[str, List[str]] = {}

        for m in memories:
            m_id = m.get("id")
            title = m.get("title", "Untitled")
            for person in m.get("people_involved", []):
                p_clean = person.strip().title()
                if p_clean:
                    people_map.setdefault(p_clean, []).append(title)
            place = m.get("location_name")
            if place:
                places_map.setdefault(place.strip().title(), []).append(title)

        connections = {
            "shared_people": [
                {"person": k, "memories": v, "frequency": len(v)}
                for k, v in people_map.items() if len(v) >= 1
            ],
            "shared_places": [
                {"place": k, "memories": v, "frequency": len(v)}
                for k, v in places_map.items() if len(v) >= 1
            ]
        }
        return connections


# Global singleton instance
memory_processor = MemoryProcessor()
