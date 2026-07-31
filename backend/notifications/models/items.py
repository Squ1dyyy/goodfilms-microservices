import datetime
from typing import Optional
from sqlalchemy import Integer, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from notifications.models.base import Base
from notifications.app.enums.notification import NotificationType, NotificationStatus


class NotificationModel(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    movie_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    type: Mapped[NotificationType] = mapped_column(String(50), nullable=False)
    url_link: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus),
        default=NotificationStatus.PENDING_MOVIE,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )

    def __str__(self) -> str:
        return f"Notification #{self.id} (User #{self.user_id} ➔ {self.type})"
