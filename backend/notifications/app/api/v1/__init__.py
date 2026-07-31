from fastapi import APIRouter

from notifications.app.api.v1 import notification

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(notification.router)

__all__ = ["api_router"]
