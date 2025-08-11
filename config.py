"""
Configuration settings for the Employee Onboarding Automation System.
This module contains environment-specific configurations, database URIs, API keys,
and other configuration parameters for the application.
Handles development, testing, and production environments through environment variables.
"""

import os
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Union
from pydantic import BaseSettings, Field, validator

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
LOG_DIR = BASE_DIR / "logs"

# Ensure required directories exist
for directory in [UPLOAD_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# Environment configuration
class Settings(BaseSettings):
    """Application settings with environment variable support."""
    # App core settings
    APP_NAME: str = "Employee Onboarding Automation System"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Automate and optimize employee onboarding processes"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")
    
    # Security settings
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings
    DATABASE_URL: str = Field(default="sqlite:///./onboarding.db")
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    
    # AWS settings
    AWS_REGION: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    
    # Email settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: str = "noreply@onboardingsystem.com"
    EMAILS_FROM_NAME: str = "Onboarding System"
    
    # Document processing settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_DOCUMENT_TYPES: List[str] = ["application/pdf", "image/jpeg", "image/png"]
    
    # Workflow settings
    WORKFLOW_DEFINITIONS_PATH: Path = BASE_DIR / "workflows" / "definitions"
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Path = LOG_DIR / "app.log"
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str, values: Dict) -> str:
        """Validate and possibly modify the database URL based on environment."""
        if values.get("ENVIRONMENT") == "test":
            return "sqlite:///./test_onboarding.db"
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def validate_cors_origins(cls, v: Union[str, List[str]], values: Dict) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            import json
            return json.loads(v)
        return v
    
    class Config:
        """Pydantic config for Settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Environment-specific overrides
if settings.ENVIRONMENT == "production":
    # Production-specific settings
    settings.DEBUG = False
    settings.CORS_ORIGINS = ["https://onboarding.example.com"]
    # Set more restrictive security settings
    
elif settings.ENVIRONMENT == "development":
    # Development-specific settings
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
    
elif settings.ENVIRONMENT == "test":
    # Testing-specific settings
    settings.DEBUG = True
    settings.DATABASE_URL = "sqlite:///./test_onboarding.db"
    settings.LOG_LEVEL = "DEBUG"

# Constants for application use
DOCUMENT_TYPES = {
    "IDENTIFICATION": "identification",
    "TAX_FORM": "tax_form",
    "CONTRACT": "contract",
    "BENEFITS": "benefits",
}

ONBOARDING_STATUSES = {
    "PENDING": "pending",
    "IN_PROGRESS": "in_progress",
    "COMPLETED": "completed",
    "REJECTED": "rejected",
}

# Feature flags
FEATURES = {
    "AI_DOCUMENT_PROCESSING": os.getenv("FEATURE_AI_DOCUMENT_PROCESSING", "false").lower() == "true",
    "AUTOMATED_BACKGROUND_CHECK": os.getenv("FEATURE_AUTOMATED_BACKGROUND_CHECK", "false").lower() == "true",
    "DIGITAL_SIGNATURES": os.getenv("FEATURE_DIGITAL_SIGNATURES", "true").lower() == "true",
    "INTEGRATION_HRIS": os.getenv("FEATURE_INTEGRATION_HRIS", "false").lower() == "true",
}