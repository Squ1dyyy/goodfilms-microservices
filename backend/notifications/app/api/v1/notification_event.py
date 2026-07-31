from faststream.rabbit import RabbitRouter, RabbitExchange, RabbitQueue, ExchangeType
from notifications.app.schemas.notification import (
    NotificationSchema,
    MovieCreatedEventSchema,
    CreateSiteNotificationSchema,
)
from notifications.app.service import notification_service
from notifications.app.enums.notification import NotificationType, NotificationStatus

from notifications.database.context import AsyncSessionLocal
from notifications.app.service.notification_service import NotificationService
from notifications.app.repository.cache.notification_redis_repository import (
    NotificationRedisRepository,
)
import notifications.core.redis_config as redis_cfg

rabbit_router = RabbitRouter()


@rabbit_router.subscriber("notifications")
async def handle_notification(data: NotificationSchema):
    await notification_service.handle(data)


films_exchange = RabbitExchange(name="films", type=ExchangeType.TOPIC)
films_queue = RabbitQueue(name="films-notifications", routing_key="movie.created")
films_update_queue = RabbitQueue(
    name="films-update-notifications", routing_key="movie.updated"
)


@rabbit_router.subscriber(queue=films_queue, exchange=films_exchange)
async def handle_movie_created(data: MovieCreatedEventSchema):
    cache = NotificationRedisRepository(redis_cfg.redis_client)
    async with AsyncSessionLocal() as session:
        service = NotificationService(session, cache)

        user_ids = await service.get_all_known_users()
        if user_ids:
            await service.create_notifications(
                user_ids=user_ids,
                notification_type=NotificationType.NEW_MOVIE,
                url_link=f"/movies/{data.movie_id}",
                movie_id=data.movie_id,
                status=NotificationStatus.PENDING_DELIVERY,
            )


@rabbit_router.subscriber(queue=films_update_queue, exchange=films_exchange)
async def handle_movie_updated(data: MovieCreatedEventSchema):
    cache = NotificationRedisRepository(redis_cfg.redis_client)
    async with AsyncSessionLocal() as session:
        service = NotificationService(session, cache)
        await service.release_movie_notifications(data.movie_id)


@rabbit_router.subscriber("site-notifications")
async def handle_site_notification(data: CreateSiteNotificationSchema):
    cache = NotificationRedisRepository(redis_cfg.redis_client)
    async with AsyncSessionLocal() as session:
        service = NotificationService(session, cache)
        await service.create_notification(
            user_id=data.user_id,
            notification_type=data.type,
            url_link=data.url_link,
            movie_id=data.movie_id,
            status=data.status,
        )
