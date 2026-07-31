from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    from notifications.models.base import Base
    from notifications.database.context import engine
    import notifications.core.redis_config as redis_cfg
    from notifications.app.broker.rabbit_broker import broker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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

    from notifications.app.api.v1 import api_router
    from notifications.app.broker.rabbit_broker import broker
    from notifications.app.api.v1.notification_event import rabbit_router

    app.include_router(api_router)

    broker.include_router(rabbit_router)
    return app
