"""Main FastAPI application module for Price Sentinel.

Provides the primary web service entrypoint, API routing, startup health checks,
and background orchestration triggers for competitor e-commerce monitoring.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.cache import cache
from src.config import settings
from src.database import Base, engine, get_db
from src.logger import logger
from src.models import PriceHistory, Product
from src.scraper import PriceScraper


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


class ScrapeRequest(BaseModel):
    """Request schema for triggering a competitor product scrape."""

    sku: str
    url: HttpUrl


@app.post("/api/v1/scrape", status_code=status.HTTP_201_CREATED)
async def trigger_scrape(payload: ScrapeRequest, db: Session = Depends(get_db)) -> dict:
    """Trigger asynchronous scraping of a competitor product URL and persist results."""
    target_url_str = str(payload.url)
    logger.info(
        f"Received scrape request for SKU: {payload.sku} | URL: {target_url_str}"
    )

    scraper = PriceScraper(headless=True)
    try:
        scraped_data = await scraper.scrape_product(target_url_str)
    except Exception as e:
        logger.error(f"Scraping failed for URL {target_url_str}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to scrape target URL: {e}",
        ) from e

    try:
        # Check if product already exists in database
        product = db.query(Product).filter(Product.sku == payload.sku).first()
        if product:
            product.name = scraped_data["name"]
            product.target_url = target_url_str
            product.current_price = scraped_data["current_price"]
            product.in_stock = scraped_data["in_stock"]
        else:
            product = Product(
                sku=payload.sku,
                name=scraped_data["name"],
                target_url=target_url_str,
                current_price=scraped_data["current_price"],
                in_stock=scraped_data["in_stock"],
            )
            db.add(product)

        db.commit()
        db.refresh(product)

        # Record price history point
        history_entry = PriceHistory(
            product_id=product.id,
            price=scraped_data["current_price"],
            in_stock=scraped_data["in_stock"],
        )
        db.add(history_entry)
        db.commit()

        # Cache latest price in Redis
        cache_key = f"product:{payload.sku}:latest"
        cache.set(
            cache_key,
            str(scraped_data["current_price"]),
            expire_seconds=3600,
        )

        logger.info(f"Successfully processed and persisted SKU: {payload.sku}")
        return {
            "status": "success",
            "sku": payload.sku,
            "name": product.name,
            "current_price": product.current_price,
            "in_stock": product.in_stock,
        }

    except Exception as db_err:
        logger.error(f"Database persistence error for SKU {payload.sku}: {db_err}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during product persistence",
        ) from db_err


@app.get("/api/v1/products", status_code=status.HTTP_200_OK)
async def list_products(db: Session = Depends(get_db)) -> list[dict]:
    """Retrieve all tracked products and their current pricing status."""
    try:
        products = db.query(Product).all()
        return [
            {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "target_url": p.target_url,
                "current_price": p.current_price,
                "in_stock": p.in_stock,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in products
        ]
    except Exception as e:
        logger.error(f"Error listing products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving products from database",
        ) from e
