import asyncio
from typing import Annotated, Optional, Callable, Awaitable, Union
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from redis.asyncio import Redis
from slowapi.errors import RateLimitExceeded
from slowapi.wrappers import Limit
from sqlalchemy.ext.asyncio import AsyncSession

from auth.app.service.auth_service import AuthService
from auth.app.repository.cache.session_redis_repository import SessionRedisRepository
from auth.app.repository.cache.reset_token_redis_repository import (
    ResetTokenRedisRepository,
)
from auth.app.repository.cache.verify_code_redis_repository import (
    VerifyCodeRedisRepository,
)
from auth.app.service import user_service
from auth.database.context import get_db, get_redis
from auth.models.items import UserModel
from auth.core import security
from auth.core.limiter import limiter, key_by_ip
from auth.exception.exceptions import NotFound

SessionDep = Annotated[AsyncSession, Depends(get_db)]

bearer_scheme = HTTPBearer(auto_error=False, description="Paste JWT access token")

CredentialsDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]


def _extract_token(creds: Optional[HTTPAuthorizationCredentials]) -> str:
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return creds.credentials


async def get_current_user(
    session: SessionDep,
    creds: CredentialsDep,
) -> UserModel:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = _extract_token(creds)
    try:
        user_id = security.decode_access_token(token)
    except JWTError:
        raise credentials_exc

    try:
        return await user_service.get_user(session, user_id)
    except NotFound:
        raise credentials_exc


CurrentUser = Annotated[UserModel, Depends(get_current_user)]


async def verify_admin_role(user: CurrentUser) -> None:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden: admin role required",
        )


async def get_session_redis(
    redis: Redis = Depends(get_redis),
) -> SessionRedisRepository:
    return SessionRedisRepository(redis)


async def get_reset_redis(
    redis: Redis = Depends(get_redis),
) -> ResetTokenRedisRepository:
    return ResetTokenRedisRepository(redis)


async def get_verify_redis(
    redis: Redis = Depends(get_redis),
) -> VerifyCodeRedisRepository:
    return VerifyCodeRedisRepository(redis)


SessionRedisDep = Annotated[SessionRedisRepository, Depends(get_session_redis)]
ResetRedisDep = Annotated[ResetTokenRedisRepository, Depends(get_reset_redis)]
VerifyRedisDep = Annotated[VerifyCodeRedisRepository, Depends(get_verify_redis)]


def get_auth_service_light(
    session_redis: SessionRedisDep,
    reset_redis: ResetRedisDep,
    verify_redis: VerifyRedisDep,
) -> AuthService:
    """Open only Redis"""
    return AuthService(
        session=None,
        session_redis=session_redis,
        reset_redis=reset_redis,
        verify_redis=verify_redis,
    )


def get_auth_service_full(
    session: SessionDep,
    session_redis: SessionRedisDep,
    reset_redis: ResetRedisDep,
    verify_redis: VerifyRedisDep,
) -> AuthService:
    """Open DB and Redis"""
    return AuthService(
        session=session,
        session_redis=session_redis,
        reset_redis=reset_redis,
        verify_redis=verify_redis,
    )


AuthLightServiceDep = Annotated[AuthService, Depends(get_auth_service_light)]
"""Open only Redis"""
AuthFullServiceDep = Annotated[AuthService, Depends(get_auth_service_full)]
"""Open DB and Redis"""


class AsyncRateLimiter:
    def __init__(
        self,
        limit_str: str,
        key_provider: Callable[[Request], Union[str, Awaitable[str]]],
    ):
        self.limit_str = limit_str
        self.key_provider = key_provider

    async def __call__(
        self,
        request: Request,
    ):
        custom_key_or_coro = self.key_provider(request)
        if isinstance(custom_key_or_coro, str):
            custom_key = custom_key_or_coro
        else:
            custom_key = await custom_key_or_coro

        from limits import parse

        limit_item = parse(self.limit_str)

        namespace = request.url.path

        is_allowed = limiter.limiter.hit(limit_item, custom_key, namespace)

        if not is_allowed:
            limit = Limit(
                limit=limit_item,
                key_func=lambda: "",
                scope=None,
                per_method=False,
                methods=None,
                error_message=None,
                exempt_when=None,
                cost=1,
                override_defaults=False,
            )
            raise RateLimitExceeded(limit)


def RateLimitDep(limit_str: str, by=key_by_ip):
    return Depends(AsyncRateLimiter(limit_str, key_provider=by))
