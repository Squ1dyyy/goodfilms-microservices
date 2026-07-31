from typing import Optional
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from movie.models.items import (
    MoviesModel,
    PersonsModel,
    MoviePersonsModel,
)


async def get_persons(
    session: AsyncSession,
    search: Optional[str],
    limit: int,
    page: int,
) -> tuple[list[PersonsModel], int]:
    offset = (page - 1) * limit
    stmt = select(PersonsModel.id)
    if search:
        stmt = stmt.where(PersonsModel.full_name.ilike(f"%{search}%"))

    total = await session.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    paged_ids = await session.execute(
        stmt.order_by(PersonsModel.id).limit(limit).offset(offset)
    )
    ids = [row[0] for row in paged_ids.all()]

    if not ids:
        return [], total

    persons_stmt = (
        select(PersonsModel).where(PersonsModel.id.in_(ids)).order_by(PersonsModel.id)
    )
    persons = (await session.execute(persons_stmt)).scalars().all()
    return list(persons), total


async def get_person(
    session: AsyncSession,
    person_id: int,
) -> Optional[PersonsModel]:
    person = await session.execute(
        select(PersonsModel).where(PersonsModel.id == person_id)
    )
    return person.scalar_one_or_none()


async def get_person_movies(
    session: AsyncSession,
    person_id: int,
    limit: int,
    page: int,
) -> tuple[list[MoviesModel], int]:
    offset = (page - 1) * limit

    id_stmt = (
        select(MoviesModel.id)
        .join(MoviePersonsModel, MoviePersonsModel.movie_id == MoviesModel.id)
        .where(MoviePersonsModel.person_id == person_id)
        .distinct()
    )

    total = (
        await session.scalar(select(func.count()).select_from(id_stmt.subquery())) or 0
    )

    paged_ids = await session.execute(
        id_stmt.order_by(MoviesModel.id).limit(limit).offset(offset)
    )
    ids = [row[0] for row in paged_ids.all()]

    if not ids:
        return [], total

    movies_stmt = (
        select(MoviesModel)
        .options(
            selectinload(MoviesModel.genres),
            selectinload(MoviesModel.studios),
            selectinload(MoviesModel.media_type_rel),
        )
        .where(MoviesModel.id.in_(ids))
        .order_by(MoviesModel.id)
    )
    movies = (await session.execute(movies_stmt)).scalars().all()

    return list(movies), total


async def create_person(
    session: AsyncSession,
    full_name: str,
    birth_date: Optional[date] = None,
    photo_url: Optional[str] = None,
) -> PersonsModel:
    new_person = PersonsModel(
        full_name=full_name,
        birth_date=birth_date,
        photo_url=photo_url,
    )
    session.add(new_person)
    await session.commit()
    await session.refresh(new_person)
    return new_person


async def patch_person(
    session: AsyncSession,
    person_id: int,
    full_name: Optional[str] = None,
    birth_date: Optional[date] = None,
    photo_url: Optional[str] = None,
) -> Optional[PersonsModel]:
    person = await get_person(session, person_id)
    if person is None:
        return None

    if full_name is not None:
        person.full_name = full_name
    if birth_date is not None:
        person.birth_date = birth_date
    if photo_url is not None:
        person.photo_url = photo_url

    session.add(person)
    await session.commit()
    await session.refresh(person)
    return person


async def delete_person(
    session: AsyncSession,
    person_id: int,
) -> Optional[PersonsModel]:
    person = await get_person(session, person_id)
    if person is None:
        return None

    await session.delete(person)
    await session.commit()
    return person
