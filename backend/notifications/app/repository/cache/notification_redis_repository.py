import json
from typing import Optional, List
from monorepo.shared.repository.redis_repository import GenericRedisRepository
from notifications.app.schemas.notification import NotificationSiteSchema


class NotificationRedisRepository(GenericRedisRepository[NotificationSiteSchema]):
    prefix = "notification:"
    model_class = NotificationSiteSchema

    async def save_user_notifications(
        self,
        user_id,
        limit,
        page,
        notifications: List[NotificationSiteSchema],
        ttl: int,
    ) -> None:
        key = f"{self.prefix}{user_id}:{limit}:{page}"
        raw = json.dumps([item.model_dump() for item in notifications])
        await self.set(key, raw, ttl=ttl)

    async def get_user_notifications(
        self, user_id, limit, page
    ) -> Optional[List[NotificationSiteSchema]]:
        key = f"{self.prefix}{user_id}:{limit}:{page}"
        raw = await self.get(key)
        if raw is None:
            return None
        return [NotificationSiteSchema.model_validate(item) for item in json.loads(raw)]

    async def delete_user_notifications(self, user_id, limit, page) -> None:
        key = f"{self.prefix}{user_id}:{limit}:{page}"
        await self.delete(key)

    async def invalidate_user_notifications(self, user_id: int) -> None:
        keys = await self.redis.keys(f"{self.prefix}{user_id}:*")
        if keys:
            await self.delete(keys)
