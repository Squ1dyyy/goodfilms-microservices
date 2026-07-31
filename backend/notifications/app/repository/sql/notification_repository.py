from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Sequence

from notifications.models.items import NotificationModel
from notifications.app.enums.notification import NotificationType, NotificationStatus


async def get_user_notifications(
    session: AsyncSession,
    user_id: int,
    limit: int,
    page: int,
) -> Sequence[NotificationModel]:
    offset = (page - 1) * limit
    stmt = (
        select(NotificationModel)
        .where(NotificationModel.user_id == user_id)
        .where(NotificationModel.status == NotificationStatus.PENDING_DELIVERY)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    notifications = result.scalars().all()

    return notifications


async def mark_notification_as_read(
    session: AsyncSession, user_id: int, notification_id: int
) -> bool:
    stmt = (
        update(NotificationModel)
        .where(NotificationModel.user_id == user_id)
        .where(NotificationModel.id == notification_id)
        .where(NotificationModel.status == NotificationStatus.PENDING_DELIVERY)
        .values(status=NotificationStatus.DELIVERED)
        .returning(NotificationModel.id)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one_or_none() is not None


async def mark_all_notifications_as_read(session: AsyncSession, user_id: int) -> bool:
    stmt = (
        update(NotificationModel)
        .where(NotificationModel.user_id == user_id)
        .where(NotificationModel.status == NotificationStatus.PENDING_DELIVERY)
        .values(status=NotificationStatus.DELIVERED)
        .returning(NotificationModel.id)
    )
    result = await session.execute(stmt)
    await session.commit()
    return len(result.scalars().all()) > 0


async def delete_notification(
    session: AsyncSession, user_id: int, notification_id: int
) -> bool:
    stmt = (
        delete(NotificationModel)
        .where(NotificationModel.user_id == user_id)
        .where(NotificationModel.id == notification_id)
        .returning(NotificationModel.id)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one_or_none() is not None


async def create_notification(
    session: AsyncSession,
    user_id: int,
    notification_type: NotificationType,
    url_link: str,
    movie_id: Optional[int] = None,
    status: NotificationStatus = NotificationStatus.PENDING_MOVIE,
) -> NotificationModel:
    db_notification = NotificationModel(
        user_id=user_id,
        movie_id=movie_id,
        type=notification_type,
        url_link=url_link,
        status=status,
    )
    session.add(db_notification)
    await session.commit()
    return db_notification


async def create_notifications(
    session: AsyncSession,
    user_ids: List[int],
    notification_type: NotificationType,
    url_link: str,
    movie_id: Optional[int] = None,
    status: NotificationStatus = NotificationStatus.PENDING_MOVIE,
) -> List[NotificationModel]:
    db_notifications = [
        NotificationModel(
            user_id=user_id,
            movie_id=movie_id,
            type=notification_type,
            url_link=url_link,
            status=status,
        )
        for user_id in user_ids
    ]
    session.add_all(db_notifications)
    await session.commit()
    return db_notifications


async def release_movie_notifications(
    session: AsyncSession,
    movie_id: int,
) -> Sequence[NotificationModel]:
    query = (
        select(NotificationModel)
        .where(NotificationModel.movie_id == movie_id)
        .where(NotificationModel.status == NotificationStatus.PENDING_MOVIE)
    )
    result = await session.execute(query)
    notifications = result.scalars().all()

    if not notifications:
        return []

    for notif in notifications:
        notif.status = NotificationStatus.PENDING_DELIVERY

    await session.commit()
    return notifications


async def get_all_known_users(session: AsyncSession) -> Sequence[int]:
    query = select(NotificationModel.user_id).distinct()
    result = await session.execute(query)
    return result.scalars().all()
