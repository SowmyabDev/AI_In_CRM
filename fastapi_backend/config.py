"""
Configuration management for E-Commerce CRM Chatbot.
Centralizes all environment-based and default settings for the application.
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or defaults.
    Use `settings = Settings()` to access throughout the app.
    """
    # API metadata
    API_TITLE: str = Field(default="E-Commerce CRM Chatbot API", description="API title")
    API_VERSION: str = Field(default="1.0.0", description="API version")
    API_DESCRIPTION: str = Field(default="AI-powered e-commerce customer support chatbot with staffing analytics", description="API description")
    DEBUG: bool = Field(default=False, env="DEBUG", description="Enable debug mode")

    # Server
    HOST: str = Field(default="127.0.0.1", env="HOST", description="Host address")
    PORT: int = Field(default=8000, env="PORT", description="Port number")

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./chatbot.db", env="DATABASE_URL", description="Database connection URL")
    DATABASE_BACKUP_DIR: str = Field(default="./backups", env="DATABASE_BACKUP_DIR", description="Backup directory")

    # LLM/Ollama
    OLLAMA_URL: str = Field(default="http://localhost:11434/api/generate", env="OLLAMA_URL", description="Ollama API endpoint")
    # Recommended: 'mistral' (best free open LLM for chatbots), fallback: 'phi3:mini', 'llama2', 'neural-chat'
    LLM_MODEL: str = Field(default="mistral", env="LLM_MODEL", description="LLM model name (e.g., mistral, phi3:mini, llama2, neural-chat)")
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE", description="LLM temperature (creativity)")
    LLM_TIMEOUT: int = Field(default=30, env="LLM_TIMEOUT", description="LLM request timeout (seconds)")

    # Frontend
    FRONTEND_URL: str = Field(default="http://localhost:5000", env="FRONTEND_URL", description="Frontend base URL")

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:5000", "http://127.0.0.1:5000"],
        env="ALLOWED_ORIGINS",
        description="Allowed CORS origins"
    )

    # Analytics & simulation
    ANALYTICS_FILE: str = Field(default="chatbot_metrics.json", env="ANALYTICS_FILE", description="Analytics metrics file")
    QUERIES_PER_HOUR_BASELINE: float = Field(default=20.0, env="QUERIES_PER_HOUR_BASELINE", description="Baseline queries per hour for simulation")

    # Session & security
    SESSION_TIMEOUT_MINUTES: int = Field(default=60, env="SESSION_TIMEOUT_MINUTES", description="Session timeout in minutes")
    MAX_REQUEST_SIZE: int = Field(default=1_000_000, env="MAX_REQUEST_SIZE", description="Max request size in bytes")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE", description="Rate limit per minute")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL", description="Logging level")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE", description="Log file path (optional)")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
