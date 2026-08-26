"""
MemoryBox Data Models & Schemas
Defines Pydantic v2 schemas for memories, interview sessions, legacy handover, and heritage analytics.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class EmotionScores(BaseModel):
    joy: float = Field(default=0.0, ge=0.0, le=1.0, description="Joy and celebration level")
    sadness: float = Field(default=0.0, ge=0.0, le=1.0, description="Grief, longing, or hardship level")
    nostalgia: float = Field(default=0.0, ge=0.0, le=1.0, description="Warm sentimentality and remembrance level")
    wonder: float = Field(default=0.0, ge=0.0, le=1.0, description="Awe, curiosity, or reverence level")
    pride: float = Field(default=0.0, ge=0.0, le=1.0, description="Cultural or familial pride level")


class SensoryDetails(BaseModel):
    sight: List[str] = Field(default_factory=list, description="Visual memories (e.g. golden mustard fields)")
    smell: List[str] = Field(default_factory=list, description="Olfactory memories (e.g. petrichor, cardamom, woodsmoke)")
    sound: List[str] = Field(default_factory=list, description="Auditory memories (e.g. temple bells, train whistle)")
    taste: List[str] = Field(default_factory=list, description="Gustatory memories (e.g. grandmother's payasam)")
    touch: List[str] = Field(default_factory=list, description="Tactile memories (e.g. rough khadi cloth)")


class MemoryCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    raw_text: str = Field(..., min_length=5, description="Oral transcript or written memory")
    recorded_by: Optional[str] = Field(default="Family Elder", max_length=100)
    language: Optional[str] = Field(default="English", description="Original language or dialect (e.g. Hindi, Telugu, Bhojpuri)")
    media_urls: List[str] = Field(default_factory=list, description="Photos, audio recordings, or document URLs in GCS")
    tags: List[str] = Field(default_factory=list)


class MemoryItem(BaseModel):
    id: str = Field(..., description="Unique Firestore Document ID")
    user_id: str = Field(..., description="Vault owner ID")
    title: str
    raw_transcript: str
    story_narrative: str = Field(..., description="Cohesive first-person story woven by Gemini")
    era: str = Field(default="Unspecified", description="Decade or historical era (e.g. 1960s, Pre-Independence)")
    year: Optional[int] = Field(default=None, description="Identified or estimated year")
    location_name: Optional[str] = Field(default=None, description="City, village, or landmark")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    people_involved: List[str] = Field(default_factory=list, description="Names and relations mentioned")
    sensory_details: SensoryDetails = Field(default_factory=SensoryDetails)
    cultural_traditions: List[str] = Field(default_factory=list, description="Rituals, recipes, festivals, crafts")
    language: str = Field(default="English")
    emotions: EmotionScores = Field(default_factory=EmotionScores)
    tags: List[str] = Field(default_factory=list)
    media_urls: List[str] = Field(default_factory=list)
    conflicts_detected: List[str] = Field(default_factory=list, description="Cross-check contradictions or historical inconsistencies")
    author_age_during_memory: Optional[int] = Field(default=None, description="Estimated or calculated age of the elder when the memory occurred")
    age_context: Optional[str] = Field(default=None, description="Contextual note e.g. 'You were approximately 14 years old'")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# --- User Profile & Authentication Models ---

class UserProfile(BaseModel):
    uid: str = Field(..., description="Firebase/Firestore User ID")
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=0, le=130, description="Mandatory age field for generational archiving")
    email: str
    phone: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    emailVerified: bool = False
    phoneVerified: bool = False
    mfaEnabled: bool = True


class SignUpRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=0, le=130, description="User age (mandatory)")
    email: str = Field(..., description="Valid email address")
    phone: str = Field(..., description="Mobile number in +91xxxxxxxxxx format")
    password: str = Field(..., min_length=8, description="Minimum 8 characters with letters & numbers")


class LoginRequest(BaseModel):
    email: str
    password: str


class VerifyOTPRequest(BaseModel):
    user_id: Optional[str] = None
    uid: Optional[str] = None
    otp_code: Optional[str] = None
    email_otp: Optional[str] = None
    sms_otp: Optional[str] = None
    otp: Optional[str] = None

    def get_uid(self) -> str:
        return self.user_id or self.uid or ""

    def get_otp(self) -> str:
        return self.otp_code or self.email_otp or self.sms_otp or self.otp or ""


class ResendOTPRequest(BaseModel):
    user_id: Optional[str] = None
    uid: Optional[str] = None

    def get_uid(self) -> str:
        return self.user_id or self.uid or ""


class AuthResponse(BaseModel):
    message: str
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    token_type: str = "bearer"
    requires_otp: bool = False
    user_data: Optional[Dict[str, Any]] = None


# --- Interviewer Models ---

class InterviewExchange(BaseModel):
    turn: int = Field(..., ge=1, le=8)
    user_response: str
    follow_up_questions: List[str] = Field(default_factory=list, description="3 distinct follow-up questions generated by Gemini")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InterviewSession(BaseModel):
    session_id: str
    user_id: str
    topic_hint: Optional[str] = Field(default="Family Heritage Story")
    exchanges: List[InterviewExchange] = Field(default_factory=list)
    current_turn: int = 1
    max_turns: int = 8
    is_completed: bool = False
    current_questions: List[str] = Field(default_factory=list)
    final_story: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StartInterviewRequest(BaseModel):
    initial_thought: Optional[str] = Field(
        default="I want to tell a story about my childhood.",
        description="The opening statement or topic from the elder"
    )
    language: Optional[str] = Field(default="English", description="Interview language")


class InterviewResponseRequest(BaseModel):
    session_id: str
    user_response: str = Field(..., min_length=1, description="Elder's spoken or typed answer")


class FinishInterviewRequest(BaseModel):
    session_id: str
    custom_title: Optional[str] = None


# --- Grounded Q&A Models ---

class AskQuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Question asked of the ancestral vault")
    era_filter: Optional[str] = None


class VaultCitation(BaseModel):
    memory_id: str
    memory_title: str
    excerpt: str


class AskQuestionResponse(BaseModel):
    answer: str
    grounded: bool
    citations: List[VaultCitation] = Field(default_factory=list)
    related_people: List[str] = Field(default_factory=list)
    related_places: List[str] = Field(default_factory=list)


# --- Governance & Legacy Handover Models ---

class CustodianInfo(BaseModel):
    custodian_name: str
    custodian_email: str
    relationship: str
    designated_date: datetime = Field(default_factory=datetime.utcnow)
    confirmation_due_date: datetime = Field(description="7-day security confirmation deadline")
    is_confirmed: bool = False
    status: str = Field(default="Pending 7-Day Confirmation")


class LegacyHandoverRequest(BaseModel):
    custodian_name: str = Field(..., min_length=2)
    custodian_email: str = Field(..., min_length=5)
    relationship: str = Field(..., min_length=2)


class DigitalHealthScoreResponse(BaseModel):
    completion_percentage: int = Field(..., ge=0, le=100)
    total_memories: int
    eras_covered: List[str]
    people_preserved: int
    places_mapped: int
    traditions_documented: int
    status_summary: str
