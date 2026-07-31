from fastapi import APIRouter

from movie.app.api.v1 import movie, person, genre, studio, country, profession

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(movie.router)
api_router.include_router(movie.admin_router)

api_router.include_router(person.router)
api_router.include_router(person.admin_router)

api_router.include_router(genre.router)
api_router.include_router(genre.admin_router)

api_router.include_router(studio.router)
api_router.include_router(studio.admin_router)

api_router.include_router(country.router)
api_router.include_router(country.admin_router)

api_router.include_router(profession.router)
api_router.include_router(profession.admin_router)
