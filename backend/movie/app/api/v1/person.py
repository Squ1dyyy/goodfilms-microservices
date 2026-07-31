from typing import Annotated
from fastapi import APIRouter, Depends, status, Query

from movie.app.api.v1.dependencies import (
    PersonFullDep,
    PaginationDep,
    verify_admin_role,
)
from movie.app.schemas.person import (
    PersonSchema,
    PersonMoviesSchema,
    CreatePersonSchema,
    UpdatePersonSchema,
    PersonQueryParams,
)
from movie.app.schemas.base import PaginatedResponseSchema
from movie.app.api.v1 import film_event

router = APIRouter(prefix="/persons", tags=["person"])
admin_router = APIRouter(prefix="/admin/persons", tags=["person-admin"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_persons(
    params: Annotated[PersonQueryParams, Query()],
    pagination: PaginationDep,
    person_service: PersonFullDep,
) -> PaginatedResponseSchema[PersonSchema]:
    return await person_service.get_persons(
        params.search, pagination.limit, pagination.page
    )


@router.get("/{person_id:int}", status_code=status.HTTP_200_OK)
async def get_person(
    person_id: int,
    person_service: PersonFullDep,
) -> PersonSchema:
    person = await person_service.get_person(person_id)
    return person


@router.get("/{person_id:int}/movies", status_code=status.HTTP_200_OK)
async def get_person_movies(
    person_id: int,
    pagination: PaginationDep,
    person_service: PersonFullDep,
) -> PersonMoviesSchema:
    return await person_service.get_person_movies(
        person_id, pagination.limit, pagination.page
    )


@admin_router.post(
    "",
    response_model=PersonSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin_role)],
)
async def create_person(
    data: CreatePersonSchema,
    person_service: PersonFullDep,
) -> PersonSchema:
    person = await person_service.create_person(
        data.full_name, data.birth_date, data.photo_url
    )
    await film_event.publish_person_created(person.id, person.full_name)
    return person


@admin_router.patch(
    "/{person_id:int}",
    response_model=PersonSchema,
    dependencies=[Depends(verify_admin_role)],
)
async def patch_person(
    person_id: int,
    data: UpdatePersonSchema,
    person_service: PersonFullDep,
) -> PersonSchema:
    person = await person_service.patch_person(
        person_id, data.full_name, data.birth_date, data.photo_url
    )
    await film_event.publish_person_updated(person.id, person.full_name)
    return person


@admin_router.delete(
    "/{person_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def delete_person(
    person_id: int,
    person_service: PersonFullDep,
) -> None:
    await person_service.delete_person(person_id)
    await film_event.publish_person_deleted(person_id)
