"""
Application configuration loaded from environment variables.
Falls back to SQLite for local development without Docker.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database — falls back to SQLite if PostgreSQL is unavailable
    DATABASE_URL: str = "sqlite:///./nobleprism.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:4173,http://localhost:8080,http://127.0.0.1:8080"

    # Velocity / kill-switch thresholds
    VELOCITY_WINDOW_SECONDS: int = 120        # 2-minute rolling window
    VELOCITY_MAX_TRANSACTIONS: int = 20       # kill switch triggers at > 20 tx in window

    KILL_SWITCH_RISK_THRESHOLD: float = 0.85  # auto-escalate above this

    ENVIRONMENT: str = "development"

    # OpenRouter stays backend-only; never expose this value to Vite.
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "deepseek/deepseek-chat-v3"
    OPENROUTER_TIMEOUT_SECONDS: float = 12.0
    OPENROUTER_MAX_RETRIES: int = 2
    OPENROUTER_CACHE_TTL_SECONDS: int = 300

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
