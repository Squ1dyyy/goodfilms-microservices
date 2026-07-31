from fastapi import APIRouter

from auth.app.api.v1 import auth, user_admin

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(user_admin.router)

__all__ = ["api_router"]
