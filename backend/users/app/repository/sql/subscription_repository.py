from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from users.models.items import PersonSubscriptionModel


async def subscribe_to_person(
    session: AsyncSession,
    user_id: int,
    person_id: int,
) -> PersonSubscriptionModel:
    query = (
        select(PersonSubscriptionModel)
        .where(PersonSubscriptionModel.user_id == user_id)
        .where(PersonSubscriptionModel.person_id == person_id)
    )
    result = await session.execute(query)
    sub = result.scalar_one_or_none()
    if sub:
        return sub

    sub = PersonSubscriptionModel(user_id=user_id, person_id=person_id)
    session.add(sub)
    await session.commit()
    return sub


async def unsubscribe_from_person(
    session: AsyncSession,
    user_id: int,
    person_id: int,
) -> bool:
    stmt = (
        delete(PersonSubscriptionModel)
        .where(PersonSubscriptionModel.user_id == user_id)
        .where(PersonSubscriptionModel.person_id == person_id)
        .returning(PersonSubscriptionModel.id)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one_or_none() is not None


async def get_person_subscriptions(
    session: AsyncSession,
    user_id: int,
) -> Sequence[int]:
    query = select(PersonSubscriptionModel.person_id).where(
        PersonSubscriptionModel.user_id == user_id
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_users_subscribed_to_person(
    session: AsyncSession,
    person_id: int,
) -> Sequence[int]:
    query = select(PersonSubscriptionModel.user_id).where(
        PersonSubscriptionModel.person_id == person_id
    )
    result = await session.execute(query)
    return result.scalars().all()
