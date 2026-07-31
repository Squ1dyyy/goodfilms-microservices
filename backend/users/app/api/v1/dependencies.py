from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing_extensions import Annotated, Optional
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from users.database.context import get_db
from users.core import security
from users.app.service.subscription_service import SubscriptionService
from users.app.service.bookmark_service import BookmarkService

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


async def get_subscription_service(
    session: SessionDep,
) -> SubscriptionService:
    return SubscriptionService(session=session)


SubscriptionServiceDep = Annotated[
    SubscriptionService, Depends(get_subscription_service)
]


async def get_bookmark_service(
    session: SessionDep,
) -> BookmarkService:
    return BookmarkService(session=session)


BookmarkServiceDep = Annotated[BookmarkService, Depends(get_bookmark_service)]
