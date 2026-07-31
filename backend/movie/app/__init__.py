from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from slowapi.errors import RateLimitExceeded

from movie.core.limiter import limiter
from movie.app.broker.rabbit_broker import broker
from movie.app.api.v1 import api_router
import movie.core.redis_config as redis_cfg


async def safe_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": f"Слишком много запросов. Превышен лимит: {exc.detail}"},
    )


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
    app.add_exception_handler(RateLimitExceeded, safe_rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app
