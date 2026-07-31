from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from users.models.base import Base


class PersonSubscriptionModel(Base):
    __tablename__ = "person_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    person_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    def __str__(self) -> str:
        return (
            f"Subscription #{self.id} (User #{self.user_id} ➔ Person #{self.person_id})"
        )


class MovieBookmarkModel(Base):
    __tablename__ = "movie_bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    movie_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    def __str__(self) -> str:
        return f"Bookmark #{self.id} (User #{self.user_id} ➔ Movie #{self.movie_id})"
