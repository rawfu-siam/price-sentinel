"""Main FastAPI application module for Price Sentinel.

Provides the primary web service entrypoint, API routing, startup health checks,
and background orchestration triggers for competitor e-commerce monitoring.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

# from pydantic import BaseModel, HttpUrl
from src.cache import cache
from src.config import settings
from src.database import Base, engine
from src.logger import logger

# from src.models import PriceHistory, Product
# from src.scraper import PriceScraper


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
