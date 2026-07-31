from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie.models.items import CountriesModel


async def get_all_countries(session: AsyncSession) -> list[CountriesModel]:
    result = await session.execute(select(CountriesModel))
    return list(result.scalars().all())


async def get_or_create_country(
    session: AsyncSession, country_name: str
) -> CountriesModel:
    result = await session.execute(
        select(CountriesModel).where(CountriesModel.name == country_name)
    )
    existing_country = result.scalar_one_or_none()

    if existing_country:
        return existing_country

    new_country = CountriesModel(name=country_name)
    session.add(new_country)
    await session.commit()
    await session.refresh(new_country)
    return new_country


async def patch_country(
    session: AsyncSession, id: int, new_country_name: str
) -> Optional[CountriesModel]:
    result = await session.execute(
        select(CountriesModel).where(CountriesModel.id == id)
    )
    existing_country = result.scalar_one_or_none()

    if existing_country is None:
        return

    existing_country.name = new_country_name
    session.add(existing_country)
    await session.commit()
    await session.refresh(existing_country)
    return existing_country


async def delete_country(session: AsyncSession, id: int) -> Optional[CountriesModel]:
    result = await session.execute(
        select(CountriesModel).where(CountriesModel.id == id)
    )
    existing_country = result.scalar_one_or_none()
    if existing_country is None:
        return

    await session.delete(existing_country)
    await session.commit()
    return existing_country
