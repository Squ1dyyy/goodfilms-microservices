from fastapi import APIRouter

from reviews.app.api.v1 import review

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(review.router)
api_router.include_router(review.admin_router)
