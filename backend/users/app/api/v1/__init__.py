from fastapi import APIRouter
from users.app.api.v1 import user

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user.router)

__all__ = ["api_router"]
