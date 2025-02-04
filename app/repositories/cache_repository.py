from typing import Optional, Any, TypeVar, Generic
import json
from redis import asyncio as aioredis
from ..config import settings
from ..interfaces.repositories.cache_repository import ICacheRepository

T = TypeVar('T')

class RedisCacheRepository(ICacheRepository[T]):
    """Redis implementation of cache repository."""
    
    def __init__(self, redis_client: aioredis.Redis, namespace: str):
        self.redis = redis_client
        self.prefix = f"{settings.REDIS_KEY_PREFIX}{namespace}:"
        self.default_ttl = settings.REDIS_CACHE_TTL

    def _get_key(self, key: str) -> str:
        """Get prefixed cache key."""
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> Optional[T]:
        """Get value from cache."""
        data = await self.redis.get(self._get_key(key))
        return json.loads(data) if data else None

    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        key = self._get_key(key)
        ttl = ttl if ttl is not None else self.default_ttl
        await self.redis.set(key, json.dumps(value), ex=ttl)

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        await self.redis.delete(self._get_key(key))

    async def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern."""
        pattern = self._get_key(pattern)
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)