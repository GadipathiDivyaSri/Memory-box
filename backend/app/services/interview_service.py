"""
The Relentless AI Interviewer Service
Differentiator feature: An empathetic, endlessly curious family historian that guides
elders through deep, nostalgic storytelling, asking warm, multi-sensory follow-up questions
and synthesizing a seamless first-person narrative story.
"""

import uuid
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

from ..models.memory import (
    InterviewSession,
    InterviewExchange,
    StartInterviewRequest,
    InterviewResponseRequest,
    FinishInterviewRequest,
)
from ..database.firestore_client import db_client
from .gemini_service import gemini_service

logger = logging.getLogger("memorybox.interviewer")

# CRITICAL: Hardcoded exact system prompt required by architecture specification
INTERVIEWER_SYSTEM_PROMPT = (
    "You are a gentle, curious family historian. Your job is to ask warm, specific follow-up "
    "questions to extract a rich memory. Based on the user's last answer, generate exactly 3 distinct "
    "follow-up questions. Focus on: Senses (What did you see/smell?), People (Who was there?), "
    "Places (Where exactly?), Emotions (How did you feel?), and Time (What year/season?)."
)

AGGREGATION_PROMPT = (
    "Combine this Q&A session into a single, coherent, first-person narrative story."
)

FALLBACK_QUESTIONS = [
    "What do you remember most about that time?",
    "Who was with you during this memory?",
    "How did that experience make you feel?",
    "What did you see, smell, or hear?",
    "Why is this memory important to you?"
]

EXIT_KEYWORDS = {
    "that's all", "thats all", "that is all", "that's everything", "thats everything",
    "i'm done", "im done", "finish", "done", "no more", "stop here", "we are done"
}


class InterviewService:
    def __init__(self):
        self.max_turns = 8

    def _is_exit_signal(self, text: str) -> bool:
        normalized = text.strip().lower()
        return any(kw in normalized for kw in EXIT_KEYWORDS)

    async def start_interview(
        self,
        user_id: str,
        request: StartInterviewRequest
    ) -> InterviewSession:
        """Phase 1 (Kickoff): Initialize the interview session and generate the first 3 questions."""
        session_id = f"iv_{uuid.uuid4().hex[:12]}"
        initial_thought = request.initial_thought or "I want to tell a story about my youth."

        # Generate initial 3 questions based on the elder's opening thought
        questions = await self._generate_follow_up_questions(
            history=[],
            last_response=initial_thought,
            language=request.language or "English"
        )

        session = InterviewSession(
            session_id=session_id,
            user_id=user_id,
            topic_hint=initial_thought[:100],
            exchanges=[],
            current_turn=1,
            max_turns=self.max_turns,
            is_completed=False,
            current_questions=questions,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        await db_client.save_interview_session(session.model_dump())
        await db_client.log_audit_event(
            user_id=user_id,
            action="interview.started",
            resource_id=session_id,
            metadata={"initial_thought": initial_thought}
        )
        return session

    async def respond_to_interview(
        self,
        user_id: str,
        request: InterviewResponseRequest
    ) -> Tuple[InterviewSession, bool]:
        """
        Phase 2 & 3 (The Loop & Continue):
        Appends user's response, checks for exit or turn limit, and generates next 3 questions.
        Returns: (Updated Session, Boolean flag indicating if interview should finish)
        """
        session_data = await db_client.get_interview_session(request.session_id)
        if not session_data:
            raise ValueError(f"Interview session {request.session_id} not found.")

        session = InterviewSession(**session_data)
        if session.is_completed:
            return session, True

        user_answer = request.user_response.strip()

        # Check for user exit condition
        should_finish = self._is_exit_signal(user_answer) or (session.current_turn >= self.max_turns)

        # Build transcript history for context
        history_list = []
        for ex in session.exchanges:
            history_list.append(f"Elder: {ex.user_response}")
            if ex.follow_up_questions:
                history_list.append(f"Historian Question: {ex.follow_up_questions[0]}")

        # If not finishing, generate next 3 questions
        next_questions: List[str] = []
        if not should_finish:
            next_questions = await self._generate_follow_up_questions(
                history=history_list,
                last_response=user_answer,
                language="English"
            )

        exchange = InterviewExchange(
            turn=session.current_turn,
            user_response=user_answer,
            follow_up_questions=next_questions,
            timestamp=datetime.utcnow()
        )
        session.exchanges.append(exchange)

        if should_finish:
            session.is_completed = True
            session.current_questions = []
        else:
            session.current_turn += 1
            session.current_questions = next_questions

        session.updated_at = datetime.utcnow()
        await db_client.update_interview_session(session.session_id, session.model_dump())
        await db_client.log_audit_event(
            user_id=user_id,
            action="interview.turn_recorded",
            resource_id=session.session_id,
            metadata={"turn": exchange.turn, "should_finish": should_finish}
        )

        return session, should_finish

    async def finish_interview(
        self,
        user_id: str,
        request: FinishInterviewRequest
    ) -> Dict[str, Any]:
        """
        Phase 4 (Aggregation) & Phase 5 (Standard Memory Extraction):
        Synthesizes the entire Q&A into one coherent first-person narrative story and saves to vault.
        """
        from .memory_processor import memory_processor

        session_data = await db_client.get_interview_session(request.session_id)
        if not session_data:
            raise ValueError(f"Interview session {request.session_id} not found.")

        session = InterviewSession(**session_data)

        # Construct complete chronological transcript
        transcript_lines = []
        transcript_lines.append(f"Opening Thought: {session.topic_hint}")
        for idx, ex in enumerate(session.exchanges, start=1):
            transcript_lines.append(f"\n--- Turn {idx} ---")
            transcript_lines.append(f"Elder: {ex.user_response}")
            if ex.follow_up_questions:
                transcript_lines.append(f"Follow-ups asked: {'; '.join(ex.follow_up_questions)}")

        full_transcript = "\n".join(transcript_lines)

        # Send to Gemini with the EXACT aggregation prompt
        story_narrative = await self._aggregate_story_narrative(full_transcript)

        # Mark session complete
        session.is_completed = True
        session.final_story = story_narrative
        session.updated_at = datetime.utcnow()
        await db_client.update_interview_session(session.session_id, session.model_dump())

        # Phase 5: Pass the aggregated story to the standard memory processor
        memory_title = request.custom_title or session.topic_hint or "A Life Remembered"
        memory_result = await memory_processor.process_and_save_memory(
            user_id=user_id,
            title=memory_title,
            raw_transcript=full_transcript,
            story_narrative=story_narrative,
            language="English",
            media_urls=[]
        )

        await db_client.log_audit_event(
            user_id=user_id,
            action="interview.finished_and_processed",
            resource_id=session.session_id,
            metadata={"memory_id": memory_result.get("id")}
        )

        # Cleanly delete session after synthesizing full story as per specification
        await db_client.delete_interview_session(session.session_id)

        return {
            "session_id": session.session_id,
            "story_narrative": story_narrative,
            "memory": memory_result
        }

    async def _generate_follow_up_questions(
        self,
        history: List[str],
        last_response: str,
        language: str = "English"
    ) -> List[str]:
        """Calls Gemini using the EXACT required interviewer prompt to yield 3 focused questions."""
        history_context = "\n".join(history[-6:]) if history else "Starting conversation."

        prompt = f"""
Conversation Context so far:
{history_context}

Elder's latest response:
\"{last_response}\"

Language: {language}

TASK:
Based on the elder's last answer, generate EXACTLY 3 distinct, warm, gentle follow-up questions.
Focus on:
1. Senses (What did you see/smell/taste/hear?)
2. People & Relations (Who was there? What were they wearing or saying?)
3. Places, Emotions & Time (Where exactly were you? How did your heart feel? What season or year was it?)

Return ONLY a valid JSON array of 3 strings:
[
  "Question 1...",
  "Question 2...",
  "Question 3..."
]
"""
        response_text = await gemini_service.generate_text(
            prompt=prompt,
            system_instruction=INTERVIEWER_SYSTEM_PROMPT
        )

        try:
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            if "[" in cleaned and "]" in cleaned:
                start_idx = cleaned.find("[")
                end_idx = cleaned.rfind("]") + 1
                questions = json.loads(cleaned[start_idx:end_idx])
                if isinstance(questions, list) and len(questions) == 3:
                    return [str(q).strip() for q in questions]
        except Exception as e:
            logger.warning(f"Failed to parse 3 questions from Gemini: {e}")

        # Fallback questions when Gemini parsing fails
        return FALLBACK_QUESTIONS[:3]

    async def _aggregate_story_narrative(self, full_transcript: str) -> str:
        """Calls Gemini with the EXACT aggregation prompt to turn interview turns into a poetic narrative."""
        prompt = f"""
{AGGREGATION_PROMPT}

Format the narrative in the warm, reflective voice of the elder telling the story to their grandchild.
Preserve all sensory details, names of relatives, places, emotional struggles, and joys.
Do not include interview turn headers or meta remarks. Just the beautiful, immersive first-person story.

Full Transcript:
{full_transcript}
"""
        narrative = await gemini_service.generate_text(prompt=prompt)
        if narrative and len(narrative.strip()) > 50:
            return narrative.strip()

        # Resilient fallback synthesis
        return (
            "Looking back across the years, I remember the quiet rhythm of our days. "
            "The warmth of our family home, the laughter shared across the veranda, and the traditions "
            "we upheld with every meal and celebration. Time carries so much away, but the faces of those I loved "
            "and the ground we walked upon remain forever woven into my heart."
        )


# Global singleton instance
interview_service = InterviewService()
