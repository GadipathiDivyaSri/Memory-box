"""
MemoryBox Application Configuration
Production settings management using Pydantic Settings and environment variables.
"""

from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "MemoryBox Digital Heritage Vault"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8080

    # Google Cloud & Gemini AI
    GOOGLE_CLOUD_PROJECT: str = "memorybox-heritage-vault"
    GOOGLE_API_KEY: str = Field(default="", description="Gemini 1.5 Flash API Key")
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Google Cloud Storage
    GCS_BUCKET_NAME: str = "memorybox-heritage-media"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # Firebase & Firestore
    FIREBASE_PROJECT_ID: str = "memorybox-heritage-vault"
    FIREBASE_CREDENTIALS_PATH: str = ""
    FIRESTORE_DATABASE_ID: str = "(default)"

    # Google Speech & Text-To-Speech
    GOOGLE_SPEECH_LANGUAGE_CODE: str = "en-IN"
    GOOGLE_TTS_VOICE_NAME: str = "en-IN-Wavenet-D"

    # Google Maps Platform
    GOOGLE_MAPS_API_KEY: str = ""

    # Security, JWT & 2FA
    JWT_SECRET_KEY: str = "memorybox-heritage-vault-production-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    TWO_FACTOR_ISSUER: str = "MemoryBoxVault"

    # Governance & Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    MAX_AUDIO_SIZE_BYTES: int = 52428800   # 50 MB
    MAX_PHOTO_SIZE_BYTES: int = 20971520   # 20 MB
    MAX_VIDEO_SIZE_BYTES: int = 209715200  # 200 MB

    # CORS Origins
    CORS_ORIGINS: str = "http://localhost:8501,http://127.0.0.1:8501,https://*.streamlit.app"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
