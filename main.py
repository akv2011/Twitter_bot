"""
Main FastAPI application for Twitter Bot
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import get_settings
from src.api.auth import router as auth_router
from src.api.tweets import router as tweets_router
from src.api.config import router as config_router
from src.services.scheduler_service import get_scheduler
from src.database.models import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Twitter Bot application...")
    
    # Initialize database
    create_tables()
    logger.info("Database tables created/verified")
    
    # Start scheduler
    scheduler = get_scheduler()
    await scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # Cleanup
    await scheduler.stop()
    logger.info("Scheduler stopped")
    logger.info("Shutting down Twitter Bot application...")


# Initialize FastAPI app
app = FastAPI(
    title="Twitter Bot API",
    description="Automated Twitter bot with AI-powered content generation and engagement",
    version="1.0.0",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {
        "message": "Twitter Bot API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "debug": settings.debug,
        "environment": "development" if settings.debug else "production"
    }


# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(tweets_router, prefix="/tweets", tags=["tweets"])
app.include_router(config_router, prefix="/config", tags=["configuration"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )