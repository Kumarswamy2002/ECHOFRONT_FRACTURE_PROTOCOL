import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "ECHOFRONT: Fracture Protocol Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server Host & Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security & JWT Tokens
    SECRET_KEY: str = "ECHOFRONT_FRACTURE_PROTOCOL_PRODUCTION_SECRET_KEY_SUPER_SECURE_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 2  # 2 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30       # 30 days
    GAME_SERVER_SECRET_TOKEN: str = "ECHOFRONT_GS_NODE_AUTHENTICATOR_TOKEN_9981"

    # Database Configuration (Supports PostgreSQL & Fallback Async SQLite)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "echofront_db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None

    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5500",
        "http://localhost:8080"
    ]

    # Game Server Cluster
    MAX_MATCH_PLAYERS: int = 24
    MIN_MATCH_PLAYERS: int = 12
    SERVER_TICK_RATE: int = 60
    MATCH_DURATION_SECONDS: int = 1200 # 20 minutes

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Return async sqlite for standalone dev if postgres isn't running or specified
        return f"sqlite+aiosqlite:///./echofront_dev.db"

    @property
    def get_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

settings = Settings()
