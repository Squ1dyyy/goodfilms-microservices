from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from auth.core.limiter import limiter
from auth.app.broker.rabbit_broker import broker
from auth.app.api.v1 import api_router
import auth.core.redis_config as redis_cfg


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_cfg.pool = redis_cfg.create_pool()

    async with Redis(connection_pool=redis_cfg.pool) as client:
        redis_cfg.redis_client = client

        await broker.start()
        try:
            yield
        finally:
            await broker.close()

    if redis_cfg.pool:
        await redis_cfg.pool.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app
