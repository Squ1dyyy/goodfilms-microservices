from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from users.app.repository.sql.bookmark_repository import (
    add_bookmark,
    remove_bookmark,
    get_bookmarks,
)
from users.app.broker.rabbit_broker import broker
from users.app.schemas.notification import CreateSiteNotificationSchema
from users.app.enums.notification import NotificationType, NotificationStatus


class BookmarkService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_bookmark(self, user_id: int, movie_id: int) -> None:
        await add_bookmark(self.session, user_id, movie_id)

        await broker.publish(
            message=CreateSiteNotificationSchema(
                user_id=user_id,
                type=NotificationType.NEW_MOVIE,
                url_link=f"/movies/{movie_id}",
                movie_id=movie_id,
                status=NotificationStatus.PENDING_MOVIE,
            ),
            queue="site-notifications",
        )

    async def remove_bookmark(self, user_id: int, movie_id: int) -> bool:
        return await remove_bookmark(self.session, user_id, movie_id)

    async def get_bookmarks(self, user_id: int) -> List[int]:
        res = await get_bookmarks(self.session, user_id)
        return list(res)
