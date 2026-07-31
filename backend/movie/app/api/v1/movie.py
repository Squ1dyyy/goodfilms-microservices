from typing import Annotated

from fastapi import Query, status, Depends, APIRouter
from movie.core.limiter import key_by_ip
from movie.app.api.v1.dependencies import (
    RateLimitDep,
    MovieFullDep,
    PaginationDep,
    verify_admin_role,
)
from movie.app.schemas.movie import (
    MovieListItemSchema,
    MovieDetailSchema,
    MovieQueryParams,
    CreateMovieSchema,
    UpdateMovieSchema,
    AddMoviePersonSchema,
    UpdateMoviePersonSchema,
    BatchMoviesRequest,
)
from movie.app.schemas.base import PaginatedResponseSchema
from movie.app.api.v1 import film_event
from movie.app.api.v1.film_event import publish_movie_created

router = APIRouter(prefix="/movies", tags=["film"])
admin_router = APIRouter(prefix="/admin/movies", tags=["film-admin"])


@router.get("")
async def get_films(
    params: Annotated[MovieQueryParams, Query()],
    pagination: PaginationDep,
    film_service: MovieFullDep,
    _ip_limit=RateLimitDep("600/minute", by=key_by_ip),
) -> PaginatedResponseSchema[MovieListItemSchema]:
    return await film_service.get_films(params, pagination.limit, pagination.page)


@router.get("/{film_id:int}")
async def get_film_by_id(film_id: int, film_service: MovieFullDep) -> MovieDetailSchema:
    return await film_service.get_film(film_id)


@router.post("/batch", response_model=list[MovieListItemSchema])
async def get_movies_batch(
    data: BatchMoviesRequest,
    film_service: MovieFullDep,
) -> list[MovieListItemSchema]:
    return await film_service.get_movies_by_ids(data.movie_ids)


@admin_router.post(
    "",
    response_model=MovieDetailSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin_role)],
)
async def create_movie(
    data: CreateMovieSchema,
    film_service: MovieFullDep,
) -> MovieDetailSchema:
    movie = await film_service.create_movie(data)
    await film_event.publish_movie_created(
        movie.id, movie.title, movie.description, movie.release_year, movie.poster_url, movie.genres, movie.imdb_rating
    )
    return movie


@admin_router.patch(
    "/{film_id:int}",
    response_model=MovieDetailSchema,
    dependencies=[Depends(verify_admin_role)],
)
async def patch_movie(
    film_id: int,
    data: UpdateMovieSchema,
    film_service: MovieFullDep,
) -> MovieDetailSchema:
    movie = await film_service.patch_movie(film_id, data)
    await film_event.publish_movie_updated(
        movie.id, movie.title, movie.description, movie.release_year, movie.poster_url, movie.genres, movie.imdb_rating
    )
    return movie


@admin_router.delete(
    "/{film_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def delete_movie(
    film_id: int,
    film_service: MovieFullDep,
) -> None:
    movie = await film_service.delete_movie(film_id)
    await film_event.publish_movie_deleted(film_id)


@admin_router.post(
    "/{movie_id:int}/persons",
    response_model=MovieDetailSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin_role)],
)
async def add_movie_person(
    movie_id: int,
    data: AddMoviePersonSchema,
    film_service: MovieFullDep,
) -> MovieDetailSchema:
    movie = await film_service.add_movie_person(
        movie_id=movie_id,
        person_id=data.person_id,
        profession_id=data.profession_id,
        character_name=data.character_name,
        billing_order=data.billing_order,
    )
    await film_event.publish_movie_person_added(
        movie_id, data.person_id, data.profession_id
    )
    return movie


@admin_router.patch(
    "/{movie_id:int}/persons/{movie_person_id:int}",
    response_model=MovieDetailSchema,
    dependencies=[Depends(verify_admin_role)],
)
async def patch_movie_person(
    movie_id: int,
    movie_person_id: int,
    data: UpdateMoviePersonSchema,
    film_service: MovieFullDep,
) -> MovieDetailSchema:
    movie = await film_service.patch_movie_person(
        movie_id=movie_id,
        movie_person_id=movie_person_id,
        profession_id=data.profession_id,
        character_name=data.character_name,
        billing_order=data.billing_order,
    )
    return movie


@admin_router.delete(
    "/{movie_id:int}/persons/{movie_person_id:int}",
    response_model=MovieDetailSchema,
    dependencies=[Depends(verify_admin_role)],
)
async def delete_movie_person(
    movie_id: int,
    movie_person_id: int,
    film_service: MovieFullDep,
) -> MovieDetailSchema:
    movie, person_id = await film_service.delete_movie_person(movie_id, movie_person_id)
    if person_id:
        await film_event.publish_movie_person_removed(movie_id, person_id)
    return movie
