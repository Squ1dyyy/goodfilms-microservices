from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from notifications.app.enums.notification import NotificationType, NotificationStatus


class EmailSchema(BaseModel):
    email: str
    code: int


class NotificationSchema(BaseModel):
    type: NotificationType
    recipient: str
    payload: dict


class PaginationSchema(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class NotificationSiteSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: NotificationType
    url_link: str
    status: NotificationStatus
    created_at: datetime


class MovieCreatedEventSchema(BaseModel):
    movie_id: int
    title: str


class CreateSiteNotificationSchema(BaseModel):
    user_id: int
    type: NotificationType
    url_link: str
    movie_id: Optional[int] = None
    status: NotificationStatus = NotificationStatus.PENDING_DELIVERY
