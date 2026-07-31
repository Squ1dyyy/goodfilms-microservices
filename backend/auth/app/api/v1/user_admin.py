from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status

from auth.app.api.v1.dependencies import SessionDep, verify_admin_role
from auth.app.schemas.user import (
    UserDataSchema,
    AdminUpdateUserSchema,
    PaginationSchema,
    PaginatedResponseSchema,
)
from auth.app.service import user_service

router = APIRouter(
    prefix="/admin/users",
    tags=["user-admin"],
    dependencies=[Depends(verify_admin_role)],
)


@router.get("", response_model=PaginatedResponseSchema[UserDataSchema])
async def get_users(
    session: SessionDep,
    pagination: Annotated[PaginationSchema, Depends(PaginationSchema)],
    search: Optional[str] = Query(None),
) -> PaginatedResponseSchema[UserDataSchema]:
    users, total = await user_service.get_users(
        session, pagination.limit, pagination.page, search
    )
    return PaginatedResponseSchema(
        items=[UserDataSchema.model_validate(u) for u in users],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.patch("/{user_id:int}", response_model=UserDataSchema)
async def update_user(
    session: SessionDep,
    user_id: int,
    data: AdminUpdateUserSchema,
) -> UserDataSchema:
    user = await user_service.update_user(session, user_id, data.is_active, data.role)
    return UserDataSchema.model_validate(user)


@router.delete("/{user_id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    session: SessionDep,
    user_id: int,
) -> None:
    await user_service.delete_user(session, user_id)
