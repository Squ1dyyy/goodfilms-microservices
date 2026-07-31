from faststream.rabbit import RabbitRouter, RabbitExchange, RabbitQueue, ExchangeType

from users.app.schemas.notification import (
    MoviePersonAddedEventSchema,
    CreateSiteNotificationSchema,
)
from users.app.enums.notification import NotificationType
from users.app.broker.rabbit_broker import broker
from users.database.context import AsyncSessionLocal
from users.app.repository.sql.subscription_repository import get_users_subscribed_to_person

rabbit_router = RabbitRouter()

films_exchange = RabbitExchange(name="films", type=ExchangeType.TOPIC)
movie_person_added_queue = RabbitQueue(
    name="movie-person-added-users-trigger", routing_key="movie_person.added"
)


@rabbit_router.subscriber(queue=movie_person_added_queue, exchange=films_exchange)
async def handle_movie_person_added(data: MoviePersonAddedEventSchema):
    async with AsyncSessionLocal() as session:
        subscribed_users = await get_users_subscribed_to_person(session, data.person_id)

        for user_id in subscribed_users:
            await broker.publish(
                message=CreateSiteNotificationSchema(
                    user_id=user_id,
                    type=NotificationType.NEW_MOVIE,
                    url_link=f"/movies/{data.movie_id}",
                    movie_id=data.movie_id,
                ),
                queue="site-notifications",
            )
