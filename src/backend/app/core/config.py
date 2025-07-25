"""
Application configuration using pydantic-settings.
"""
from typing import List, Optional, Union
from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields from .env
    )
    
    # Project info
    PROJECT_NAME: str = "StoneSoup"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development", description="Environment (development, staging, production)")
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://stonesoup:stonesoup_dev@localhost:5432/stonesoup",
        description="PostgreSQL connection URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]
    )
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str = Field(default="", description="Clerk secret key")
    CLERK_PUBLISHABLE_KEY: str = Field(default="", description="Clerk publishable key")
    CLERK_JWT_VERIFICATION_KEY: Optional[str] = Field(None, description="Clerk JWT verification key")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    
    # OpenRouter
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API key")
    
    # Sentry
    SENTRY_DSN: Optional[str] = Field(None, description="Sentry DSN for error tracking")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(0.1, description="Sentry traces sample rate")
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = Field(None, description="Celery broker URL (defaults to REDIS_URL)")
    CELERY_RESULT_BACKEND: Optional[str] = Field(None, description="Celery result backend (defaults to REDIS_URL)")
    
    @validator("CELERY_BROKER_URL", pre=True)
    def set_celery_broker(cls, v: Optional[str], values: dict) -> str:
        return v or values.get("REDIS_URL", "")
    
    @validator("CELERY_RESULT_BACKEND", pre=True)
    def set_celery_backend(cls, v: Optional[str], values: dict) -> str:
        return v or values.get("REDIS_URL", "")


# Create settings instance
settings = Settings()