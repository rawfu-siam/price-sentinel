"""Redis cache connection and operations module.

Provides robust client management and caching helper functions for high-velocity
competitor monitoring state and rate limiting.
"""

from typing import Any, Optional

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

    def get(self, key: str) -> Optional[str]:
        """Retrieve value from cache by key."""
        if not self.client:
            logger.warning("Redis client unavailable. Skipping cache get.")
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Error retrieving key '{key}' from Redis: {e}")
            return None

    def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        """Store value in cache with optional expiration time."""
        if not self.client:
            logger.warning("Redis client unavailable. Skipping cache set.")
            return False
        try:
            self.client.set(key, value, ex=expire_seconds)
            return True
        except Exception as e:
            logger.error(f"Error setting key '{key}' in Redis: {e}")
            return False
