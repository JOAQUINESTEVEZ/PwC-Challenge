# app/utils/redis_config.py
from redis import asyncio as aioredis
from typing import Optional
from ..config import settings

# Redis connection pool
redis_pool = None

async def init_redis_pool():
    """Initialize Redis connection pool."""
    global redis_pool
    if redis_pool is None:
        connection_kwargs = {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "username": settings.REDIS_USERNAME,
            "password": settings.REDIS_PASSWORD,
            "decode_responses": settings.REDIS_DECODE_RESPONSES,
            "socket_connect_timeout": settings.REDIS_POOL_TIMEOUT,
            "socket_keepalive": True
        }

        redis_pool = aioredis.ConnectionPool(
            max_connections=settings.REDIS_POOL_SIZE,
            **connection_kwargs
        )
    return redis_pool

async def get_redis() -> aioredis.Redis:
    """Get Redis client from pool."""
    if redis_pool is None:
        await init_redis_pool()
    return aioredis.Redis(connection_pool=redis_pool)