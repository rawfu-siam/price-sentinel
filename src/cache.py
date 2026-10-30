"""Redis cache connection and operations module.

Provides robust client management and caching helper functions for high-velocity
competitor monitoring state and rate limiting.
"""

# from typing import Any, Optional

import redis

from src.config import settings
from src.logger import logger


class RedisClient:
    """Encapsulates Redis connection and cache operations with defensive handling."""

    def __init__(self) -> None:
        """Initialize Redis client using configuration settings."""
        logger.info("Initializing Redis cache client...")
        try:
            self.client = redis.Redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
            # Test connection
            self.client.ping()
            logger.info("Successfully connected to Redis cache.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
