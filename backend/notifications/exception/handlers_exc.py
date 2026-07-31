from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status
from notifications.exception.smtp_exceptions import (
    SMTPError,
    SMTPConnectionError,
    SMTPAuthError,
    SMTPRecipientError,
    SMTPSendError,
)


async def smtp_error_handler(request: Request, exc: SMTPError) -> JSONResponse:
    if isinstance(exc, SMTPConnectionError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Не удалось подключиться к SMTP серверу"},
        )

    if isinstance(exc, SMTPAuthError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Ошибка авторизации SMTP"},
        )

    if isinstance(exc, SMTPRecipientError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Неверный адрес получателя"},
        )

    if isinstance(exc, SMTPSendError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Ошибка отправки письма"},
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(SMTPError, smtp_error_handler)
