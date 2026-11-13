import json
from redis import asyncio as redis
from redis.exceptions import RedisError

from app.observability import configure_logging


class RedisJsonCache:
    """Best-effort cache: a Redis outage must never make an API request fail."""

    def __init__(self, redis_url: str | None):
        self._client = redis.from_url(redis_url, decode_responses=True) if redis_url else None
        self._logger = configure_logging("learning-pathway-service")

    async def get(self, key: str) -> dict | list | None:
        if self._client is None:
            return None
        try:
            value = await self._client.get(key)
            if value is None:
                self._logger.info("cache_miss", extra={"cache_key": key})
                return None
            self._logger.info("cache_hit", extra={"cache_key": key})
            return json.loads(value)
        except (RedisError, json.JSONDecodeError):
            self._logger.warning("cache_read_failed", extra={"cache_key": key})
            return None

    async def set(self, key: str, value: dict | list, ttl_seconds: int) -> None:
        if self._client is None:
            return
        try:
            await self._client.set(key, json.dumps(value, default=str), ex=ttl_seconds)
        except RedisError:
            self._logger.warning("cache_write_failed", extra={"cache_key": key})

    async def delete(self, key: str) -> None:
        if self._client is None:
            return
        try:
            await self._client.delete(key)
        except RedisError:
            self._logger.warning("cache_delete_failed", extra={"cache_key": key})

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
