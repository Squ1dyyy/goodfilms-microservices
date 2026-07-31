from fastapi import APIRouter, Depends, status

from movie.app.api.v1.dependencies import GenreFullDep, verify_admin_role
from movie.app.schemas.genre import (
    CreateGenreSchema,
    GenreSchema,
    UpdateGenreSchema,
)

router = APIRouter(prefix="/genres", tags=["genre"])
admin_router = APIRouter(prefix="/admin/genres", tags=["genre-admin"])


@router.get("")
async def get_all_genres(genre_service: GenreFullDep) -> list[GenreSchema]:
    return await genre_service.get_genres()


@admin_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin_role)],
)
async def create_genre(
    data: CreateGenreSchema,
    genre_service: GenreFullDep,
) -> None:
    await genre_service.create_genre(data.name)


@admin_router.patch(
    "/{genre_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def patch_genre(
    genre_id: int,
    data: UpdateGenreSchema,
    genre_service: GenreFullDep,
) -> None:
    await genre_service.patch_genre(genre_id, data.name)


@admin_router.delete(
    "/{genre_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def delete_genre(
    genre_id: int,
    genre_service: GenreFullDep,
) -> None:
    await genre_service.delete_genre(genre_id)
