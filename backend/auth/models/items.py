import datetime
from typing import Optional, List

from auth.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy_utils import EmailType, IPAddressType, CountryType


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        EmailType,
        unique=True,
        index=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    sessions: Mapped[List["SessionModel"]] = relationship(
        "SessionModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return self.username


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    device_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    device_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(IPAddressType, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(CountryType, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="sessions")

    def __str__(self) -> str:
        dev_info = f" ({self.device_name})" if self.device_name else ""
        return f"Session #{self.id} for user #{self.user_id}{dev_info}"
