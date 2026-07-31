from auth.app.broker.rabbit_broker import broker
from auth.app.enums.notification import NotificationType
from auth.app.schemas.notification import NotificationSchema


async def send_email(
    email: str,
    code: int,
) -> None:
    await broker.publish(
        NotificationSchema(
            type=NotificationType.EMAIL_VERIFICATION,
            recipient=email,
            payload={"code": code},
        ),
        queue="notifications",
    )


async def welcome_message(
    email: str,
) -> None:
    await broker.publish(
        NotificationSchema(
            type=NotificationType.WELCOME,
            recipient=email,
            payload={},
        ),
        queue="notifications",
    )


async def forgot_password(
    email: str,
    token: str,
) -> None:
    await broker.publish(
        NotificationSchema(
            type=NotificationType.PASSWORD_RESET,
            recipient=email,
            payload={"token": token},
        ),
        queue="notifications",
    )


async def send_verification(
    email: str,
    code: int,
) -> None:
    await broker.publish(
        NotificationSchema(
            type=NotificationType.EMAIL_VERIFICATION,
            recipient=email,
            payload={"code": code},
        ),
        queue="notifications",
    )
