from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from notifications.app.schemas.notification import PaginationSchema
from redis.asyncio import Redis
from typing_extensions import Annotated, Optional
from jose import JWTError

from sqlalchemy.ext.asyncio import AsyncSession
from notifications.database.context import get_db, get_redis
from notifications.core import security
from notifications.app.service.notification_service import NotificationService
from notifications.app.repository.cache.notification_redis_repository import (
    NotificationRedisRepository,
)

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


PaginationDep = Annotated[PaginationSchema, Depends(PaginationSchema)]


async def get_notification_service(
    session: SessionDep,
    redis: Redis = Depends(get_redis),
) -> NotificationService:
    return NotificationService(
        session=session, cache=NotificationRedisRepository(redis)
    )


NotificationServiceDep = Annotated[
    NotificationService, Depends(get_notification_service)
]
