"""Main FastAPI application module for Price Sentinel.

Provides the primary web service entrypoint, API routing, startup health checks,
and background orchestration triggers for competitor e-commerce monitoring.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import text

from src.cache import cache
from src.config import settings
from src.database import Base, engine
from src.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Execute startup and shutdown routines with zero-trust validation."""
    logger.info("Starting Price Sentinel API service...")
    try:
        # Create database tables if they do not exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")

        # Verify Redis connectivity
        if cache.client is None:
            logger.warning("Redis cache client is offline during startup.")
        else:
            logger.info("Redis cache connection confirmed active.")
    except Exception as e:
        logger.error(f"Critical startup error during lifespan initialization: {e}")
        raise

    yield

    logger.info("Shutting down Price Sentinel API service...")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=("High-Velocity E-Commerce Competitor Monitor & AI Automation Backend"),
    lifespan=lifespan,
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    """Perform system health check verifying database and cache status."""
    db_status = "healthy"
    redis_status = "healthy" if cache.client is not None else "degraded"

    try:
        # Quick database connectivity check
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Health check database failure: {e}")
        db_status = "unhealthy"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connectivity failure",
        ) from e

    return {
        "status": "online" if db_status == "healthy" else "degraded",
        "database": db_status,
        "redis": redis_status,
    }
