import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

import recomendations.core.redis_config as redis_cfg
from recomendations.core.embedder import run_embeddings_generator, preload_model
from recomendations.app.broker.rabbit_broker import broker
from recomendations.app.api.v1.event_handlers import rabbit_router
from recomendations.app.api.v1.recomendation import router as recommendations_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_cfg.pool = redis_cfg.create_pool()

    async with Redis(connection_pool=redis_cfg.pool) as client:
        redis_cfg.redis_client = client

        await broker.start()
        await preload_model()
        bg_task = asyncio.create_task(run_embeddings_generator())
        try:
            yield
        finally:
            bg_task.cancel()
            try:
                await bg_task
            except asyncio.CancelledError:
                pass
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

    app.include_router(recommendations_router, prefix="/api/v1")

    broker.include_router(rabbit_router)

    return app
