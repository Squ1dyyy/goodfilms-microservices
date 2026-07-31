import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel, Field

from recomendations.app.api.v1.dependencies import RecommendationServiceDep
from recomendations.app.schemas.recommendation import MovieListItemSchema, CustomRecommendationRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommendations", tags=["recommendations"])


async def get_current_user_id() -> int:
    return 1


@router.get("", status_code=status.HTTP_200_OK)
async def get_personalized_recommendations(
    user_id: int = Depends(get_current_user_id),
):
    return {"detail": "Not implemented"}


@router.get("/movies/{movie_id:int}/similar", response_model=List[MovieListItemSchema], status_code=status.HTTP_200_OK)
async def get_similar_movies(
    movie_id: int,
    service: RecommendationServiceDep,
    limit: int = Query(10, ge=1, le=10),
):
    return await service.get_similar_movies(movie_id=movie_id, limit=limit)


@router.post("/custom", response_model=List[MovieListItemSchema], status_code=status.HTTP_200_OK)
async def get_custom_recommendations(
    request: CustomRecommendationRequest,
    service: RecommendationServiceDep,
):
    return await service.get_custom_recommendations(
        movie_ids=request.movie_ids,
        genres=request.genres,
        release_year=request.release_year,
        release_year_from=request.release_year_from,
        release_year_to=request.release_year_to,
        imdb_rating_from=request.imdb_rating_from,
        media_type=request.media_type,
        custom_description=request.custom_description,
        limit=request.limit or 12
    )


