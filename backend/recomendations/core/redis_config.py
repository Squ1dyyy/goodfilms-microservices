from typing import Optional

from redis.asyncio import ConnectionPool, Redis

from recomendations.config import config
from monorepo.shared.cache.redis_pool import create_redis_pool

pool: Optional[ConnectionPool] = None
redis_client: Redis = None                


def create_pool() -> ConnectionPool:
    return create_redis_pool(config.REDIS_URL)
