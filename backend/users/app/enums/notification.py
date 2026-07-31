from enum import Enum


class NotificationType(str, Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    WELCOME = "welcome"
    NEW_MOVIE = "new_movie"


class NotificationStatus(str, Enum):
    PENDING_MOVIE = "pending_movie"
    PENDING_DELIVERY = "pending_delivery"
    DELIVERED = "delivered"
