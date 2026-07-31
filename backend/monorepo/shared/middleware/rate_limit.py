import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from redis.asyncio import Redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int = 100, time_window: int = 60):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.time_window = time_window

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        current_time = time.time()
        clear_before = current_time - self.time_window

        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        key = f"rate_limit:{client_ip}"

        pool = getattr(request.app.state, "redis_pool", None)

        if not pool:
            return await call_next(request)

        try:
            redis_client = Redis(connection_pool=pool)

            async with redis_client.pipeline(transaction=True) as pipe:
                pipe.zremrangebyscore(key, 0, clear_before).zcard(key).zadd(
                    key,
                    {str(current_time): current_time},
                ).expire(key, self.time_window + 1)

                _, current_request_count, _, _ = await pipe.execute()

            if current_request_count > self.rate_limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too Many Requests. Please try again later."},
                )

        except Exception as e:
            pass

        response = await call_next(request)
        return response
