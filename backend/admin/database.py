from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from admin.config import config

from auth.models.items import UserModel, SessionModel
from movie.models.items import (
    MoviesModel,
    CountriesModel,
    GenresModel,
    StudiosModel,
    PersonsModel,
    ProfessionsModel,
    MoviePersonsModel,
    KeywordsModel,
    MediaTypesModel,
    movie_countries,
    movie_genres,
    movie_studios,
    movie_keywords,
)
from users.models.items import PersonSubscriptionModel, MovieBookmarkModel
from notifications.models.items import NotificationModel

auth_engine = create_async_engine(config.DATABASE_URL)
movie_engine = create_async_engine(config.MOVIE_DATABASE_URL)
users_engine = create_async_engine(config.USERS_DATABASE_URL)
notifications_engine = create_async_engine(config.NOTIFICATIONS_DATABASE_URL)

binds = {
    UserModel: auth_engine,
    SessionModel: auth_engine,
    UserModel.__table__: auth_engine,
    SessionModel.__table__: auth_engine,
    MoviesModel: movie_engine,
    CountriesModel: movie_engine,
    GenresModel: movie_engine,
    StudiosModel: movie_engine,
    PersonsModel: movie_engine,
    ProfessionsModel: movie_engine,
    MoviePersonsModel: movie_engine,
    KeywordsModel: movie_engine,
    MediaTypesModel: movie_engine,
    MoviesModel.__table__: movie_engine,
    CountriesModel.__table__: movie_engine,
    GenresModel.__table__: movie_engine,
    StudiosModel.__table__: movie_engine,
    PersonsModel.__table__: movie_engine,
    ProfessionsModel.__table__: movie_engine,
    MoviePersonsModel.__table__: movie_engine,
    KeywordsModel.__table__: movie_engine,
    MediaTypesModel.__table__: movie_engine,
    movie_countries: movie_engine,
    movie_genres: movie_engine,
    movie_studios: movie_engine,
    movie_keywords: movie_engine,
    PersonSubscriptionModel: users_engine,
    MovieBookmarkModel: users_engine,
    PersonSubscriptionModel.__table__: users_engine,
    MovieBookmarkModel.__table__: users_engine,
    NotificationModel: notifications_engine,
    NotificationModel.__table__: notifications_engine,
}

AsyncSessionLocal = async_sessionmaker(
    bind=auth_engine,
    binds=binds,
    expire_on_commit=False,
)
