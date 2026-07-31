from types import ModuleType

from redis.asyncio import Redis


def make_get_redis(redis_cfg: ModuleType):
    async def get_redis() -> Redis:
        if redis_cfg.redis_client is None:
            raise RuntimeError("Async client Redis isn`t init in lifespan")
        return redis_cfg.redis_client

    return get_redis
