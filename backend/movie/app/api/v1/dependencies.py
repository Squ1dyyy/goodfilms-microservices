import asyncio
from typing import Callable, Union, Awaitable
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from redis.asyncio import Redis
from slowapi.errors import RateLimitExceeded
from slowapi.wrappers import Limit
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from typing_extensions import Annotated, Optional
from fastapi import Depends, HTTPException, Request

from movie.app.service.studio_service import StudioService
from movie.app.service.genre_service import GenreService
from movie.app.service.person_service import PersonService
from movie.app.service.country_service import CountryService
from movie.app.service.movie_service import MovieService
from movie.app.service.profession_service import ProfessionService

from movie.app.repository.cache.movie_redis_repository import MovieRedisRepository
from movie.app.repository.cache.genre_redis_repository import GenreRedisRepository
from movie.app.repository.cache.studio_redis_repository import StudioRedisRepository
from movie.app.repository.cache.person_redis_repository import PersonRedisRepository
from movie.app.repository.cache.country_redis_repository import CountryRedisRepository
from movie.app.repository.cache.profession_redis_repository import (
    ProfessionRedisRepository,
)
from movie.core.limiter import limiter, key_by_ip
from movie.app.schemas.movie import PaginationSchema
from movie.database.context import get_db, get_redis
from movie.core import security

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


async def get_user_id(creds: CredentialsDep) -> int:
    token = _extract_token(creds)
    try:
        return security.decode_access_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


UserIdDep = Annotated[int, Depends(get_user_id)]


async def verify_admin_role(creds: CredentialsDep) -> None:
    token = _extract_token(creds)
    try:
        payload = security.decode_access_token_payload(token)
        role = payload.get("role")
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="forbidden: admin role required",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


PaginationDep = Annotated[PaginationSchema, Depends(PaginationSchema)]


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


async def get_movie_service(
    session: SessionDep,
    redis: Redis = Depends(get_redis),
) -> MovieService:
    return MovieService(session=session, cache=MovieRedisRepository(redis))


async def get_genre_service(
    session: SessionDep,
    redis: Redis = Depends(get_redis),
) -> GenreService:
    return GenreService(session=session, cache=GenreRedisRepository(redis))


async def get_studio_service(
    session: SessionDep,
    redis: Redis = Depends(get_redis),
) -> StudioService:
    return StudioService(session=session, cache=StudioRedisRepository(redis))


async def get_person_service(
    session: SessionDep,
    redis: Redis = Depends(get_redis),
) -> PersonService:
    return PersonService(session=session, cache=PersonRedisRepository(redis))


async def get_country_service(
    session: SessionDep,
    redis: Redis = Depends(get_redis),
) -> CountryService:
    return CountryService(session=session, cache=CountryRedisRepository(redis))


async def get_profession_service(
    session: SessionDep,
    redis: Redis = Depends(get_redis),
) -> ProfessionService:
    return ProfessionService(session=session, cache=ProfessionRedisRepository(redis))


MovieFullDep = Annotated[MovieService, Depends(get_movie_service)]
PersonFullDep = Annotated[PersonService, Depends(get_person_service)]
GenreFullDep = Annotated[GenreService, Depends(get_genre_service)]
StudioFullDep = Annotated[StudioService, Depends(get_studio_service)]
CountryFullDep = Annotated[CountryService, Depends(get_country_service)]
ProfessionFullDep = Annotated[ProfessionService, Depends(get_profession_service)]
