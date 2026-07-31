from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis.asyncio import Redis
from typing_extensions import Annotated, Optional
from jose import JWTError

from sqlalchemy.ext.asyncio import AsyncSession
from reviews.database.context import get_db, get_redis
from reviews.core import security

from reviews.app.repository.cache.review_redis_repository import ReviewRedisRepository
from reviews.app.service.review_service import ReviewService
from reviews.app.schemas.review import PaginationSchema

SessionDep = Annotated[AsyncSession, Depends(get_db)]

bearer_scheme = HTTPBearer(auto_error=False, description="Paste JWT access token")

CredentialsDep = Annotated[
    Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)
]


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


async def verify_email_verified(creds: CredentialsDep) -> None:
    token = _extract_token(creds)
    try:
        payload = security.decode_access_token_payload(token)
        is_verified = payload.get("is_verified", False)
        if not is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not verified mail",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


PaginationDep = Annotated[PaginationSchema, Depends(PaginationSchema)]


async def get_review_service(
    session: SessionDep,
    redis: Redis = Depends(get_redis),
) -> ReviewService:
    return ReviewService(session=session, cache=ReviewRedisRepository(redis))


ReviewServiceDep = Annotated[ReviewService, Depends(get_review_service)]
