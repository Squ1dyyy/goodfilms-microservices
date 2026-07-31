from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from notifications.app.api.v1.dependencies import (
    UserIdDep,
    PaginationDep,
    NotificationServiceDep,
)
from notifications.app.schemas.notification import NotificationSiteSchema
from typing import List

router = APIRouter(prefix="/notification", tags=["notification"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_notifications(
    user_id: UserIdDep,
    pagination: PaginationDep,
    notification_service: NotificationServiceDep,
) -> Optional[List[NotificationSiteSchema]]:
    notifications = await notification_service.get_all(
        user_id, pagination.limit, pagination.page
    )
    return notifications


@router.patch("/{notification_id:int}/read", status_code=status.HTTP_200_OK)
async def mark_as_read(
    notification_id: int,
    user_id: UserIdDep,
    notification_service: NotificationServiceDep,
):
    await notification_service.mark_as_read(user_id, notification_id)
    return {"status": "success"}


@router.post("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_as_read(
    user_id: UserIdDep,
    notification_service: NotificationServiceDep,
):
    await notification_service.mark_all_read(user_id)
    return {"status": "success"}


@router.delete("/{notification_id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    user_id: UserIdDep,
    notification_service: NotificationServiceDep,
) -> None:
    await notification_service.delete(user_id, notification_id)
