from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List

from users.app.api.v1.dependencies import (
    UserIdDep,
    SubscriptionServiceDep,
    BookmarkServiceDep,
)

router = APIRouter(prefix="/users", tags=["users"])


class UserProfileUpdateSchema(BaseModel):
    nickname: Optional[str] = Field(None, min_length=3, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None


@router.get("/{user_id:int}/profile", status_code=status.HTTP_200_OK)
async def get_user_profile(user_id: int):
    """
    Get public profile details of any user.
    """
    return {"detail": "Not implemented"}


@router.patch("/me/profile", status_code=status.HTTP_200_OK)
async def update_my_profile(
    data: UserProfileUpdateSchema,
    user_id: UserIdDep,
):
    """
    Update the authenticated user's profile.
    """
    return {"detail": "Not implemented"}


@router.get("/me/bookmarks", response_model=List[int], status_code=status.HTTP_200_OK)
async def get_my_bookmarks(
    user_id: UserIdDep,
    bookmark_service: BookmarkServiceDep,
) -> List[int]:
    """
    Get user's bookmarks/watchlist.
    """
    return await bookmark_service.get_bookmarks(user_id)


@router.post("/me/bookmarks/{movie_id:int}", status_code=status.HTTP_201_CREATED)
async def add_to_bookmarks(
    movie_id: int,
    user_id: UserIdDep,
    bookmark_service: BookmarkServiceDep,
):
    """
    Add a movie to bookmarks/watchlist.
    """
    await bookmark_service.add_bookmark(user_id, movie_id)
    return {"status": "bookmarked"}


@router.delete("/me/bookmarks/{movie_id:int}", status_code=status.HTTP_200_OK)
async def remove_from_bookmarks(
    movie_id: int,
    user_id: UserIdDep,
    bookmark_service: BookmarkServiceDep,
):
    """
    Remove a movie from bookmarks/watchlist.
    """
    unbookmarked = await bookmark_service.remove_bookmark(user_id, movie_id)
    return {"status": "unbookmarked" if unbookmarked else "not_bookmarked"}


@router.get("/me/history", status_code=status.HTTP_200_OK)
async def get_watch_history(
    user_id: UserIdDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Get user's watch history.
    """
    return {"detail": "Not implemented"}


@router.post("/me/history/{movie_id:int}", status_code=status.HTTP_201_CREATED)
async def add_to_watch_history(
    movie_id: int,
    user_id: UserIdDep,
):
    """
    Record that user has watched a movie.
    """
    return {"detail": "Not implemented"}


@router.post("/subscribe/person/{person_id:int}", status_code=status.HTTP_201_CREATED)
async def subscribe_to_person(
    person_id: int,
    user_id: UserIdDep,
    subscription_service: SubscriptionServiceDep,
):
    await subscription_service.subscribe_to_person(user_id, person_id)
    return {"status": "subscribed"}


@router.delete("/subscribe/person/{person_id:int}", status_code=status.HTTP_200_OK)
async def unsubscribe_from_person(
    person_id: int,
    user_id: UserIdDep,
    subscription_service: SubscriptionServiceDep,
):
    unsubscribed = await subscription_service.unsubscribe_from_person(
        user_id, person_id
    )
    return {"status": "unsubscribed" if unsubscribed else "not_subscribed"}


@router.get(
    "/subscribe/person", response_model=List[int], status_code=status.HTTP_200_OK
)
async def get_person_subscriptions(
    user_id: UserIdDep,
    subscription_service: SubscriptionServiceDep,
) -> List[int]:
    return await subscription_service.get_person_subscriptions(user_id)
