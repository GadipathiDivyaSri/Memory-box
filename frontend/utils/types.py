"""
Typed Dataclasses and Type Hints for MemoryBox Frontend
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EmotionScoresView:
    joy: float = 0.8
    sadness: float = 0.1
    nostalgia: float = 0.9
    wonder: float = 0.5
    pride: float = 0.7


@dataclass
class MemoryItemView:
    id: str
    title: str
    summary: str
    raw_text: str
    description: str
    category: str = "Family"  # Family, Travel, College, Achievements, Events, Friends, Everyday, Work
    tags: List[str] = field(default_factory=list)
    date: str = "2026"
    year: int = 2026
    month: str = "January"
    location: str = "Home"
    people: List[str] = field(default_factory=list)
    image_url: Optional[str] = None
    voice_url: Optional[str] = None
    sentiment: str = "Nostalgic & Joyful"
    why_it_matters: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"))
    is_demo: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "raw_text": self.raw_text,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "date": self.date,
            "year": self.year,
            "month": self.month,
            "location": self.location,
            "people": self.people,
            "image_url": self.image_url,
            "voice_url": self.voice_url,
            "sentiment": self.sentiment,
            "why_it_matters": self.why_it_matters,
            "created_at": self.created_at,
            "is_demo": self.is_demo
        }


SMART_CATEGORIES = [
    {"name": "All", "icon": "✨", "color": "#8b5a2b"},
    {"name": "Family", "icon": "❤️", "color": "#b85d38"},
    {"name": "Travel", "icon": "✈️", "color": "#2e6f9e"},
    {"name": "College", "icon": "🎓", "color": "#5b4282"},
    {"name": "Achievements", "icon": "🏆", "color": "#b8860b"},
    {"name": "Events", "icon": "🎉", "color": "#c25975"},
    {"name": "Friends", "icon": "👥", "color": "#3f7a63"},
    {"name": "Everyday", "icon": "📸", "color": "#706e6b"},
    {"name": "Work", "icon": "💼", "color": "#4a5568"}
]
