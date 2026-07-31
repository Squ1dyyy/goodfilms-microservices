from fastapi import FastAPI
from sqladmin import Admin

from admin.config import config
from admin.database import auth_engine, AsyncSessionLocal
from admin.auth import AdminAuth
from admin.views import (
    UserAdmin,
    SessionAdmin,
    MoviesAdmin,
    CountriesAdmin,
    GenresAdmin,
    StudiosAdmin,
    KeywordsAdmin,
    MediaTypesAdmin,
    PersonsAdmin,
    ProfessionsAdmin,
    MoviePersonsAdmin,
    PersonSubscriptionAdmin,
    MovieBookmarkAdmin,
    NotificationAdmin,
)

app = FastAPI(title="GoodFilms Admin Dashboard")

auth_backend = AdminAuth(secret_key=config.JWT_SECRET_KEY)

admin = Admin(
    app=app,
    engine=auth_engine,
    session_maker=AsyncSessionLocal,
    authentication_backend=auth_backend,
    title="GoodFilms Admin Panel",
    base_url="/admin",
)

admin.add_view(UserAdmin)
admin.add_view(SessionAdmin)
admin.add_view(MoviesAdmin)
admin.add_view(CountriesAdmin)
admin.add_view(GenresAdmin)
admin.add_view(StudiosAdmin)
admin.add_view(KeywordsAdmin)
admin.add_view(MediaTypesAdmin)
admin.add_view(PersonsAdmin)
admin.add_view(ProfessionsAdmin)
admin.add_view(MoviePersonsAdmin)
admin.add_view(PersonSubscriptionAdmin)
admin.add_view(MovieBookmarkAdmin)
admin.add_view(NotificationAdmin)
