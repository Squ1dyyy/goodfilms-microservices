from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from monorepo.shared.exception.exceptions import (
    ServiceError,
    NotFound,
    AlreadyExists,
    InvalidCredentials,
    Forbidden,
)


async def service_error_handler(
    request: Request,
    exc: ServiceError,
) -> JSONResponse:
    if isinstance(exc, NotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )

    if isinstance(exc, AlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Resource already exists"},
        )

    if isinstance(exc, InvalidCredentials):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"},
        )

    if isinstance(exc, Forbidden):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Permission denied"},
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ServiceError, service_error_handler)
