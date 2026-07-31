from typing import Optional
from faststream.rabbit import RabbitExchange, ExchangeType
from movie.app.broker.rabbit_broker import broker
from movie.app.schemas.film_event import (
    MovieEventSchema,
    MovieDeletedEventSchema,
    PersonEventSchema,
    PersonDeletedEventSchema,
    MoviePersonAddedEventSchema,
    MoviePersonRemovedEventSchema,
)

films_exchange = RabbitExchange(name="films", type=ExchangeType.TOPIC)


async def publish_movie_created(
    movie_id: int,
    title: str,
    description: Optional[str] = None,
    release_year: Optional[int] = None,
    poster_url: Optional[str] = None,
    genres: Optional[list[str]] = None,
    imdb_rating: Optional[float] = None,
) -> None:
    await broker.publish(
        message=MovieEventSchema(
            movie_id=movie_id,
            title=title,
            description=description,
            release_year=release_year,
            poster_url=poster_url,
            genres=genres or [],
            imdb_rating=imdb_rating,
        ),
        exchange=films_exchange,
        routing_key="movie.created",
    )


async def publish_movie_updated(
    movie_id: int,
    title: str,
    description: Optional[str] = None,
    release_year: Optional[int] = None,
    poster_url: Optional[str] = None,
    genres: Optional[list[str]] = None,
    imdb_rating: Optional[float] = None,
) -> None:
    await broker.publish(
        message=MovieEventSchema(
            movie_id=movie_id,
            title=title,
            description=description,
            release_year=release_year,
            poster_url=poster_url,
            genres=genres or [],
            imdb_rating=imdb_rating,
        ),
        exchange=films_exchange,
        routing_key="movie.updated",
    )


async def publish_movie_deleted(movie_id: int) -> None:
    await broker.publish(
        message=MovieDeletedEventSchema(movie_id=movie_id),
        exchange=films_exchange,
        routing_key="movie.deleted",
    )


async def publish_person_created(
    person_id: int,
    full_name: str,
) -> None:
    await broker.publish(
        message=PersonEventSchema(person_id=person_id, full_name=full_name),
        exchange=films_exchange,
        routing_key="person.created",
    )


async def publish_person_updated(
    person_id: int,
    full_name: str,
) -> None:
    await broker.publish(
        message=PersonEventSchema(person_id=person_id, full_name=full_name),
        exchange=films_exchange,
        routing_key="person.updated",
    )


async def publish_person_deleted(person_id: int) -> None:
    await broker.publish(
        message=PersonDeletedEventSchema(person_id=person_id),
        exchange=films_exchange,
        routing_key="person.deleted",
    )


async def publish_movie_person_added(
    movie_id: int,
    person_id: int,
    profession_id: int,
) -> None:
    await broker.publish(
        message=MoviePersonAddedEventSchema(
            movie_id=movie_id,
            person_id=person_id,
            profession_id=profession_id,
        ),
        exchange=films_exchange,
        routing_key="movie_person.added",
    )


async def publish_movie_person_removed(
    movie_id: int,
    person_id: int,
) -> None:
    await broker.publish(
        message=MoviePersonRemovedEventSchema(movie_id=movie_id, person_id=person_id),
        exchange=films_exchange,
        routing_key="movie_person.removed",
    )
