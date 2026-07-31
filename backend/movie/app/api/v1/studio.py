from fastapi import APIRouter, Depends, status

from movie.app.api.v1.dependencies import StudioFullDep, verify_admin_role
from movie.app.schemas.studio import (
    StudioSchema,
    CreateStudioSchema,
    UpdateStudioSchema,
)

router = APIRouter(prefix="/studios", tags=["studio"])
admin_router = APIRouter(prefix="/admin/studios", tags=["studio-admin"])


@router.get("")
async def get_all_studios(studio_service: StudioFullDep) -> list[StudioSchema]:
    return await studio_service.get_studios()


@admin_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin_role)],
)
async def create_studio(
    data: CreateStudioSchema,
    studio_service: StudioFullDep,
) -> None:
    await studio_service.create_studio(data.name)


@admin_router.patch(
    "/{studio_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def patch_studio(
    studio_id: int,
    data: UpdateStudioSchema,
    studio_service: StudioFullDep,
) -> None:
    await studio_service.patch_studio(studio_id, data.name)


@admin_router.delete(
    "/{studio_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def delete_studio(
    studio_id: int,
    studio_service: StudioFullDep,
) -> None:
    await studio_service.delete_studio(studio_id)
