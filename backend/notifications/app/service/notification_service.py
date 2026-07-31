from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from notifications.app.service import email_service
from notifications.app.schemas.notification import NotificationSchema, NotificationType
from notifications.app.repository.cache.notification_redis_repository import (
    NotificationRedisRepository,
)
from notifications.app.repository.sql.notification_repository import (
    get_user_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    delete_notification,
    create_notification as create_sql_notification,
    create_notifications as create_sql_notifications,
    release_movie_notifications,
    get_all_known_users,
)
from notifications.app.schemas.notification import (
    NotificationSiteSchema,
    PaginationSchema,
)
from notifications.app.enums.notification import NotificationStatus
from notifications.models.items import NotificationModel


async def handle(data: NotificationSchema):
    if data.type == NotificationType.EMAIL_VERIFICATION:
        await email_service.send_verification(data.recipient, data.payload["code"])
    elif data.type == NotificationType.PASSWORD_RESET:
        await email_service.password_reset(data.recipient, data.payload["token"])
    elif data.type == NotificationType.WELCOME:
        await email_service.welcome_message(data.recipient)


class NotificationService:
    def __init__(
        self,
        session: AsyncSession,
        cache: NotificationRedisRepository,
    ):
        self.session = session
        self.cache = cache

    async def get_all(
        self,
        user_id: int,
        limit: int,
        page: int,
    ) -> list[NotificationSiteSchema]:
        notifications = await get_user_notifications(self.session, user_id, limit, page)
        if notifications:
            await self.cache.invalidate_user_notifications(user_id)
        return [NotificationSiteSchema.model_validate(n) for n in notifications]

    async def mark_as_read(
        self,
        user_id: int,
        notification_id: int,
    ) -> None:
        updated = await mark_notification_as_read(
            self.session, user_id, notification_id
        )
        if updated:
            await self.cache.invalidate_user_notifications(user_id)

    async def mark_all_read(self, user_id: int) -> None:
        updated = await mark_all_notifications_as_read(self.session, user_id)
        if updated:
            await self.cache.invalidate_user_notifications(user_id)

    async def delete(self, user_id: int, notification_id: int) -> None:
        deleted = await delete_notification(self.session, user_id, notification_id)
        if deleted:
            await self.cache.invalidate_user_notifications(user_id)

    async def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        url_link: str,
        movie_id: Optional[int] = None,
        status: NotificationStatus = NotificationStatus.PENDING_DELIVERY,
    ) -> NotificationModel:
        db_notification = await create_sql_notification(
            self.session, user_id, notification_type, url_link, movie_id, status
        )
        await self.cache.invalidate_user_notifications(user_id)
        return db_notification

    async def create_notifications(
        self,
        user_ids: List[int],
        notification_type: NotificationType,
        url_link: str,
        movie_id: Optional[int] = None,
        status: NotificationStatus = NotificationStatus.PENDING_DELIVERY,
    ) -> List[NotificationModel]:
        db_notifications = await create_sql_notifications(
            self.session, user_ids, notification_type, url_link, movie_id, status
        )
        for user_id in user_ids:
            await self.cache.invalidate_user_notifications(user_id)
        return db_notifications

    async def release_movie_notifications(
        self,
        movie_id: int,
    ) -> List[NotificationModel]:
        notifications = await release_movie_notifications(self.session, movie_id)
        for notif in notifications:
            await self.cache.invalidate_user_notifications(notif.user_id)
        return list(notifications)

    async def get_all_known_users(self) -> List[int]:
        res = await get_all_known_users(self.session)
        return list(res)
