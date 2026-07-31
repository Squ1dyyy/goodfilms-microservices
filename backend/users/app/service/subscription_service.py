from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from users.app.repository.sql.subscription_repository import (
    subscribe_to_person,
    unsubscribe_from_person,
    get_person_subscriptions,
)


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def subscribe_to_person(self, user_id: int, person_id: int) -> None:
        await subscribe_to_person(self.session, user_id, person_id)

    async def unsubscribe_from_person(self, user_id: int, person_id: int) -> bool:
        return await unsubscribe_from_person(self.session, user_id, person_id)

    async def get_person_subscriptions(self, user_id: int) -> List[int]:
        res = await get_person_subscriptions(self.session, user_id)
        return list(res)
