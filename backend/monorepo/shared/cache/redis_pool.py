from redis.asyncio import ConnectionPool


def create_redis_pool(redis_url: str) -> ConnectionPool:
    return ConnectionPool.from_url(
        redis_url,
        max_connections=20,
        decode_responses=True,
    )
