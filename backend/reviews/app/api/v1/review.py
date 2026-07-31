from fastapi import APIRouter, status, Query, Depends, HTTPException

from reviews.app.api.v1.dependencies import (
    UserIdDep,
    SessionDep,
    ReviewServiceDep,
    PaginationDep,
    verify_admin_role,
    verify_email_verified,
    CredentialsDep,
)
from reviews.app.schemas.review import (
    ReviewCreateSchema,
    ReviewResponseSchema,
    RatingCreateSchema,
    RatingSummarySchema,
    PaginatedResponseSchema,
)
from reviews.core import security

router = APIRouter(prefix="/reviews", tags=["reviews"])
admin_router = APIRouter(prefix="/admin/reviews", tags=["reviews-admin"])


@router.post(
    "/movies/{movie_id:int}",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_email_verified)],
)
async def create_review(
    movie_id: int,
    data: ReviewCreateSchema,
    user_id: UserIdDep,
    review_service: ReviewServiceDep,
) -> ReviewResponseSchema:
    review = await review_service.create_review(
        user_id=user_id,
        movie_id=movie_id,
        review=data.review,
        username=data.username,
    )
    return review


@router.get("/movies/{movie_id:int}", status_code=status.HTTP_200_OK)
async def get_movie_reviews(
    movie_id: int,
    pagination: PaginationDep,
    review_service: ReviewServiceDep,
) -> PaginatedResponseSchema[ReviewResponseSchema]:
    reviews = await review_service.get_reviews(
        movie_id, pagination.last_id, pagination.limit
    )
    return reviews


@router.delete("/{review_id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    user_id: UserIdDep,
    creds: CredentialsDep,
    review_service: ReviewServiceDep,
):
    review = await review_service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = security.decode_access_token_payload(creds.credentials)
        role = payload.get("role")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if role not in ("admin", "moderator") and review.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden: you do not have permission to delete this review",
        )

    await review_service.delete_review(review_id)


@admin_router.delete(
    "/{review_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def delete_review_as_admin(
    review_id: int,
    review_service: ReviewServiceDep,
):
    deleted = await review_service.delete_review(review_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )


@router.put("/movies/{movie_id:int}/rating", status_code=status.HTTP_200_OK)
async def rate_movie(
    movie_id: int,
    data: RatingCreateSchema,
    user_id: UserIdDep,
    review_service: ReviewServiceDep,
):
    if movie_id != data.movie_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie ID in path and body must match",
        )
    await review_service.rate_movie(
        user_id=user_id, movie_id=movie_id, rating=data.rating
    )
    return {"detail": "Rating submitted successfully"}


@router.get(
    "/movies/{movie_id:int}/ratings",
    response_model=RatingSummarySchema,
    status_code=status.HTTP_200_OK,
)
async def get_movie_ratings_summary(
    movie_id: int,
    review_service: ReviewServiceDep,
):
    return await review_service.get_ratings_summary(movie_id)
