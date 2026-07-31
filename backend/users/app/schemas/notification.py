from typing import Optional
from pydantic import BaseModel
from users.app.enums.notification import NotificationType, NotificationStatus


class CreateSiteNotificationSchema(BaseModel):
    user_id: int
    type: NotificationType
    url_link: str
    movie_id: Optional[int] = None
    status: NotificationStatus = NotificationStatus.PENDING_DELIVERY


class MoviePersonAddedEventSchema(BaseModel):
    movie_id: int
    person_id: int
    profession_id: int
