"""
MemoryBox FastAPI Application Entrypoint
Production-grade backend built for Google Cloud Run and Firebase.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .routers import auth, memories, interview, ask, timeline, map
from .database.firestore_client import db_client
from .utils.rate_limiter import limiter
from .exceptions import http_exception_handler, validation_exception_handler
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.exceptions import RequestValidationError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("memorybox.main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes environment validation and demo archival data if database is fresh."""
    from .utils.env_check import validate_environment
    validate_environment()
    logger.info("Initializing MemoryBox Digital Heritage Vault...")
    # Seed high-fidelity sample heritage stories for immediate demonstration
    existing = await db_client.list_memories(user_id="elder_heritage_keeper_1", limit=1)
    if not existing:
        sample_memories = [
            {
                "id": "mem_childhood_monsoon",
                "user_id": "elder_heritage_keeper_1",
                "title": "Monsoon Afternoons in the Courtyard",
                "raw_transcript": "In 1968, in our ancestral house in Mysore, the first monsoon rains would make the courtyard red clay tiles sizzle. Grandmother would brew hot spiced ginger tea.",
                "story_narrative": "Looking back to 1968 in Mysore, I still remember the sweet, dusty scent of the earth when the first monsoon showers hit our red clay courtyard tiles. The heavy raindrops sounded like temple drums upon the roof. Grandmother Lakshmi would sit by the brass woodstove, grinding fresh cardamom and dried ginger into simmering buffalo milk. My cousins and I would float paper boats made of old school notebooks down the veranda gutters, our laughter mingling with the rain.",
                "era": "1960s",
                "year": 1968,
                "location_name": "Mysore, Karnataka",
                "latitude": 12.2958,
                "longitude": 76.6394,
                "people_involved": ["Grandmother Lakshmi", "Uncle Raghavan", "Cousin Meena"],
                "sensory_details": {
                    "sight": ["Red clay tiled courtyard glistening with rainwater", "Paper boats floating down stone gutters"],
                    "smell": ["Petrichor on dry Deccan soil", "Simmering cardamom and ginger chai"],
                    "sound": ["Thunder like temple drums", "Rain dripping from copper gutters"],
                    "taste": ["Sweet, spicy ginger milk with jaggery"],
                    "touch": ["Cool stone veranda floor under bare feet"]
                },
                "cultural_traditions": ["Monsoon welcoming tea ritual", "Handmade paper boat racing"],
                "language": "Kannada & English",
                "emotions": {"joy": 0.88, "sadness": 0.05, "nostalgia": 0.98, "wonder": 0.70, "pride": 0.80},
                "tags": ["1960s", "Monsoon", "Childhood", "Mysore", "Grandmother"],
                "media_urls": [],
                "conflicts_detected": [],
                "created_at": "2026-08-20T10:00:00"
            },
            {
                "id": "mem_harvest_pongal",
                "user_id": "elder_heritage_keeper_1",
                "title": "The Golden Harvest & Sugarcane Fields",
                "raw_transcript": "During Sankranti in 1974, grandfather would wake everyone at 4 AM to harvest fresh turmeric roots and sugarcane.",
                "story_narrative": "Every winter of 1974 in Thanjavur, our village woke while the morning stars still shone bright. Grandfather Sundaram would drape his rough khadi shawl over his shoulders and lead us into the sugarcane fields. We harvested fresh yellow turmeric roots, tying sacred turmeric leaves around the new earthen cooking pot. When the sweet rice milk boiled over the rim, the entire household shouted 'Pongalo Pongal!' to welcome abundance into our home.",
                "era": "1970s",
                "year": 1974,
                "location_name": "Thanjavur, Tamil Nadu",
                "latitude": 10.7870,
                "longitude": 79.1378,
                "people_involved": ["Grandfather Sundaram", "Aunt Janaki", "Father"],
                "sensory_details": {
                    "sight": ["Dewdrops glistening on green sugarcane stalks", "Bright yellow turmeric roots"],
                    "smell": ["Woodsmoke and sweet boiling jaggery syrup"],
                    "sound": ["Chanting of harvest songs across the fields", "Crackling of dried palm leaves"],
                    "taste": ["Fresh sweet jaggery pongal cooked in clay pot"],
                    "touch": ["Rough khadi shawl against crisp morning chill"]
                },
                "cultural_traditions": ["Thai Pongal Harvest Ceremony", "Clay pot blessing ritual"],
                "language": "Tamil & English",
                "emotions": {"joy": 0.94, "sadness": 0.02, "nostalgia": 0.95, "wonder": 0.65, "pride": 0.90},
                "tags": ["1970s", "Harvest", "Pongal", "Thanjavur", "Traditions"],
                "media_urls": [],
                "conflicts_detected": [],
                "created_at": "2026-08-21T14:30:00"
            }
        ]
        for sm in sample_memories:
            await db_client.save_memory(sm)
        logger.info("Sample archival memories loaded into memory store.")

    yield
    logger.info("MemoryBox backend shutting down gracefully.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Privacy-first, AI-powered digital heritage vault for the PromptWars × Diksuchi EdTech AI Hackathon 2026.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate Limiter & Standardized Error Handling
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


# Global Exception Handler (Zero stack trace leaks)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred while preserving heritage data. Please try again later.",
            "path": request.url.path
        }
    )


# Mount Feature Routers
app.include_router(auth.router)
app.include_router(memories.router)
app.include_router(interview.router)
app.include_router(ask.router)
app.include_router(timeline.router)
app.include_router(map.router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check for Google Cloud Run container readiness."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "gemini_model": settings.GEMINI_MODEL
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "app": settings.APP_NAME,
        "hackathon": "PromptWars × Diksuchi EdTech AI Hackathon 2026",
        "theme": "AI for Social Impact",
        "documentation": "/docs"
    }
