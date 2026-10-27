
import hashlib
import json
import logging
import os
import re
from typing import Optional

import redis

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class RequestCache:
    """Redis cache for recently processed flood-relief requests."""

    def __init__(self, redis_url: Optional[str] = None):
        self.client = redis.Redis.from_url(
            redis_url or REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

    @staticmethod
    def normalize_text(text: str, location: str = "") -> str:
        """Normalize message text and location for duplicate detection."""
        normalized_text = re.sub(r"\s+", " ", text.strip().lower())
        normalized_location = re.sub(
            r"\s+", " ", location.strip().lower()
        )
        return f"{normalized_location}|{normalized_text}"

    @classmethod
    def fingerprint(cls, text: str, location: str = "") -> str:
        """Generate a stable hash for a request."""
        normalized = cls.normalize_text(text, location)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def is_duplicate(self, text: str, location: str = "") -> bool:
        """Return True if the request fingerprint is already cached."""
        key = f"floodsense:request:{self.fingerprint(text, location)}"

        try:
            return bool(self.client.exists(key))
        except redis.RedisError:
            logger.warning("Redis unavailable; skipping duplicate cache check.")
            return False

    def mark_processed(self, text: str, location: str = "") -> bool:
        """Cache a processed request fingerprint with an expiration."""
        key = f"floodsense:request:{self.fingerprint(text, location)}"

        try:
            return bool(
                self.client.set(
                    key,
                    "processed",
                    ex=CACHE_TTL_SECONDS,
                    nx=True,
                )
            )
        except redis.RedisError:
            logger.warning("Redis unavailable; request was not cached.")
            return False
    
    def claim_request(self, text: str, location: str = "") -> bool:
        """Atomically reserve a request fingerprint in Redis."""
        key = f"floodsense:request:{self.fingerprint(text, location)}"

        try:
            return bool(
                self.client.set(
                    key,
                    "processing",
                    ex=CACHE_TTL_SECONDS,
                    nx=True,
                )
            )
        except redis.RedisError:
            logger.warning("Redis unavailable; processing without cache.")
            return True

    def forget_request(self, text: str, location: str = "") -> None:
        """Remove a reservation if processing or saving fails."""
        key = f"floodsense:request:{self.fingerprint(text, location)}"

        try:
            self.client.delete(key)
        except redis.RedisError:
            logger.warning("Could not remove the Redis request key.")

    def close(self) -> None:
        """Close the Redis client."""
        self.client.close()


request_cache = RequestCache()

#- Creates a SHA-256 fingerprint from normalized request text and location.
#- Checks Redis for a previously processed fingerprint.
#- Expires cached fingerprints after five minutes by default.
#- Continues safely if Redis is unavailable.
