from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from reviews.models.items import ReviewsModel, ReviewsRatingsModel


async def create_review(
    session: AsyncSession,
    user_id: int,
    movie_id: int,
    review: str,
    username: Optional[str] = None,
) -> ReviewsModel:
    new_review = ReviewsModel(
        user_id=user_id, movie_id=movie_id, review=review, username=username
    )
    session.add(new_review)
    await session.commit()

    return new_review


async def get_reviews_by_movie_id(
    session: AsyncSession,
    movie_id: int,
    last_id: Optional[int],
    limit: int,
) -> list[ReviewsModel]:
    query = (
        select(ReviewsModel)
        .where(ReviewsModel.movie_id == movie_id)
        .order_by(ReviewsModel.id.asc())
        .limit(limit)
    )

    if last_id is not None:
        query = query.where(ReviewsModel.id > last_id)

    result = await session.execute(query)

    return list(result.scalars().all())


async def get_review_by_id(
    session: AsyncSession,
    review_id: int,
) -> Optional[ReviewsModel]:
    return await session.get(ReviewsModel, review_id)


async def delete_review(
    session: AsyncSession,
    review: ReviewsModel,
) -> None:
    await session.delete(review)
    await session.commit()


async def upsert_rating(
    session: AsyncSession,
    user_id: int,
    movie_id: int,
    rating: int,
) -> ReviewsRatingsModel:
    query = select(ReviewsRatingsModel).where(
        ReviewsRatingsModel.user_id == user_id,
        ReviewsRatingsModel.movie_id == movie_id,
    )
    result = await session.execute(query)
    db_rating = result.scalar_one_or_none()
    if db_rating:
        db_rating.rating = rating
    else:
        db_rating = ReviewsRatingsModel(
            user_id=user_id, movie_id=movie_id, rating=rating
        )
        session.add(db_rating)
    await session.commit()
    return db_rating


async def get_ratings_summary(
    session: AsyncSession,
    movie_id: int,
) -> dict:
    dist_query = (
        select(ReviewsRatingsModel.rating, func.count(ReviewsRatingsModel.id))
        .where(ReviewsRatingsModel.movie_id == movie_id)
        .group_by(ReviewsRatingsModel.rating)
    )
    dist_result = await session.execute(dist_query)
    distribution = {r: count for r, count in dist_result.all()}
    full_distribution = {i: distribution.get(i, 0) for i in range(1, 11)}

    stats_query = select(
        func.avg(ReviewsRatingsModel.rating), func.count(ReviewsRatingsModel.id)
    ).where(ReviewsRatingsModel.movie_id == movie_id)
    stats_result = await session.execute(stats_query)
    avg_val, total_val = stats_result.one()

    return {
        "average_rating": float(avg_val) if avg_val is not None else 0.0,
        "total_ratings": total_val,
        "distribution": full_distribution,
    }
