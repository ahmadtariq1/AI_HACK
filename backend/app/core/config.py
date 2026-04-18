"""
Application configuration — reads from environment variables / .env file.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # -----------------------------------------------------------------------
    # App metadata
    # -----------------------------------------------------------------------
    PROJECT_NAME: str = "AI Hack"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "FastAPI backend"
    ENVIRONMENT: str = "development"  # development | staging | production

    # -----------------------------------------------------------------------
    # API
    # -----------------------------------------------------------------------
    API_V1_STR: str = "/api/v1"

    # -----------------------------------------------------------------------
    # CORS — React dev server runs on 5173 by default (Vite)
    # -----------------------------------------------------------------------
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # CRA / other common ports
        "http://127.0.0.1:5173",
    ]

    # -----------------------------------------------------------------------
    # Database (fill in when ready)
    # -----------------------------------------------------------------------
    DATABASE_URL: str = "sqlite:///./dev.db"
    # DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"

    # -----------------------------------------------------------------------
    # Security
    # -----------------------------------------------------------------------
    SECRET_KEY: str = "changeme-use-a-long-random-string-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"

    # -----------------------------------------------------------------------
    # LLM Configuration
    # Select provider: "google" (Google AI Studio) | "ollama" (local Ollama)
    # -----------------------------------------------------------------------
    LLM_PROVIDER: str = "google"          # default: Google AI Studio

    # Google AI Studio
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.1-flash-lite-preview" # fast + cheap JSON-mode capable

    # Ollama (local)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"


settings = Settings()
