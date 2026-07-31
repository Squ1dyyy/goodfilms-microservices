from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from reviews.app.broker.rabbit_broker import broker
from reviews.app.api.v1 import api_router
import reviews.core.redis_config as redis_cfg


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app
