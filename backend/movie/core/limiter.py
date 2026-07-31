from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from movie.config import config

limiter = Limiter(key_func=get_remote_address, storage_uri=config.REDIS_URL)


def key_by_ip(request: Request) -> str:
    return get_remote_address(request)


async def key_by_email(request: Request) -> str:
    try:
        body = await request.json()
        email = body.get("email", "anon")
    except Exception:
        email = "unknown"
    return email


def key_by_user_id(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            from movie.core.security import decode_access_token

            return str(decode_access_token(auth[7:]))
        except Exception:
            pass
    return get_remote_address(request)
