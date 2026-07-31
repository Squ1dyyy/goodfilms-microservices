from fastapi import APIRouter, Depends, status

from movie.app.api.v1.dependencies import ProfessionFullDep, verify_admin_role
from movie.app.schemas.profession import (
    ProfessionSchema,
    CreateProfessionSchema,
    UpdateProfessionSchema,
)

router = APIRouter(prefix="/professions", tags=["profession"])
admin_router = APIRouter(prefix="/admin/professions", tags=["profession-admin"])


@router.get("")
async def get_all_professions(
    profession_service: ProfessionFullDep,
) -> list[ProfessionSchema]:
    return await profession_service.get_professions()


@admin_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin_role)],
)
async def create_profession(
    data: CreateProfessionSchema,
    profession_service: ProfessionFullDep,
) -> None:
    await profession_service.create_profession(data.name)


@admin_router.patch(
    "/{profession_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def patch_profession(
    profession_id: int,
    data: UpdateProfessionSchema,
    profession_service: ProfessionFullDep,
) -> None:
    await profession_service.patch_profession(profession_id, data.name)


@admin_router.delete(
    "/{profession_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def delete_profession(
    profession_id: int,
    profession_service: ProfessionFullDep,
) -> None:
    await profession_service.delete_profession(profession_id)
