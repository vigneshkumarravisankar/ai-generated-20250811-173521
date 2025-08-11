"""
Main application entry point for Employee Onboarding Automation System.
This file initializes the FastAPI application, sets up middleware,
configures routers, and handles startup/shutdown events.
"""
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from contextlib import asynccontextmanager

# Import configuration
from app.core.config import settings
from app.core.logging_config import setup_logging

# Import database
from app.db.session import engine, SessionLocal
from app.db.base import Base

# Import routers
from app.api.api_v1.api import api_router
from app.api.health import health_router

# Import authentication
from app.core.auth import get_current_active_user

# Import models for creating tables
import app.models  # noqa

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for FastAPI app lifespan.
    Handles startup and shutdown events.
    """
    # Startup operations
    logger.info("Starting up Employee Onboarding Automation System...")
    setup_logging()
    
    # Create database tables if they don't exist
    logger.info("Creating database tables if they don't exist...")
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # Uncomment for clean start
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Application startup complete.")
    yield
    
    # Shutdown operations
    logger.info("Shutting down Employee Onboarding Automation System...")
    logger.info("Application shutdown complete.")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Employee Onboarding Automation System",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI route that requires authentication in production."""
    if settings.ENVIRONMENT != "development":
        # In non-dev environments, require authentication
        user = await get_current_active_user()
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access documentation"
            )
    
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - API Documentation",
        swagger_favicon_url="/static/favicon.ico",
    )

@app.get("/", tags=["root"])
async def root():
    """Root endpoint with system information."""
    return {
        "system": "Employee Onboarding Automation System",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    """
    Run the application directly using uvicorn when the script is executed.
    Note: In production, use gunicorn with uvicorn workers instead.
    """
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )