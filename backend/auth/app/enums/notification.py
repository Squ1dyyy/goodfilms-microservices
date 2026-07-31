from enum import Enum


class NotificationType(str, Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    WELCOME = "welcome"
