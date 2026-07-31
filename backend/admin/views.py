from sqladmin import ModelView

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
)
from users.models.items import PersonSubscriptionModel, MovieBookmarkModel
from notifications.models.items import NotificationModel


class UserAdmin(ModelView, model=UserModel):
    column_list = [
        UserModel.id,
        UserModel.username,
        UserModel.email,
        UserModel.role,
        UserModel.is_active,
        UserModel.is_verified,
        UserModel.created_at,
    ]
    column_searchable_list = [UserModel.username, UserModel.email]
    column_filters = [UserModel.role, UserModel.is_active, UserModel.is_verified]
    form_excluded_columns = [UserModel.sessions]
    column_labels = {
        "id": "ID",
        "username": "Username",
        "email": "Email",
        "role": "Role",
        "is_active": "Active",
        "is_verified": "Verified",
        "created_at": "Created At",
    }
    icon = "fa-solid fa-users"
    name = "User"
    name_plural = "Users"
    category = "Authentication"


class SessionAdmin(ModelView, model=SessionModel):
    column_list = [
        SessionModel.id,
        SessionModel.user,
        SessionModel.device_name,
        SessionModel.device_type,
        SessionModel.ip_address,
        SessionModel.country,
        SessionModel.created_at,
    ]
    column_searchable_list = [
        SessionModel.device_name,
        SessionModel.ip_address,
        SessionModel.country,
    ]
    column_filters = [SessionModel.device_type, SessionModel.country]
    icon = "fa-solid fa-key"
    name = "Session"
    name_plural = "Sessions"
    category = "Authentication"


class MoviesAdmin(ModelView, model=MoviesModel):
    column_list = [
        MoviesModel.id,
        MoviesModel.title,
        MoviesModel.release_year,
        MoviesModel.runtime_minutes,
    ]
    column_searchable_list = [MoviesModel.title, MoviesModel.original_title]
    column_filters = [MoviesModel.release_year]
    form_excluded_columns = [
        MoviesModel.countries,
        MoviesModel.genres,
        MoviesModel.studios,
        MoviesModel.movie_persons,
        MoviesModel.keywords,
    ]
    icon = "fa-solid fa-film"
    name = "Movie"
    name_plural = "Movies"
    category = "Movie Directory"


class CountriesAdmin(ModelView, model=CountriesModel):
    column_list = [CountriesModel.id, CountriesModel.name]
    column_searchable_list = [CountriesModel.name]
    form_excluded_columns = [CountriesModel.movies]
    icon = "fa-solid fa-globe"
    name = "Country"
    name_plural = "Countries"
    category = "Movie Directory"


class GenresAdmin(ModelView, model=GenresModel):
    column_list = [GenresModel.id, GenresModel.name]
    column_searchable_list = [GenresModel.name]
    form_excluded_columns = [GenresModel.movies]
    icon = "fa-solid fa-tags"
    name = "Genre"
    name_plural = "Genres"
    category = "Movie Directory"


class StudiosAdmin(ModelView, model=StudiosModel):
    column_list = [StudiosModel.id, StudiosModel.name]
    column_searchable_list = [StudiosModel.name]
    form_excluded_columns = [StudiosModel.movies]
    icon = "fa-solid fa-building"
    name = "Studio"
    name_plural = "Studios"
    category = "Movie Directory"


class KeywordsAdmin(ModelView, model=KeywordsModel):
    column_list = [KeywordsModel.id, KeywordsModel.name]
    column_searchable_list = [KeywordsModel.name]
    form_excluded_columns = [KeywordsModel.movies]
    icon = "fa-solid fa-hashtag"
    name = "Keyword"
    name_plural = "Keywords"
    category = "Movie Directory"


class MediaTypesAdmin(ModelView, model=MediaTypesModel):
    column_list = [MediaTypesModel.id, MediaTypesModel.name]
    column_searchable_list = [MediaTypesModel.name]
    icon = "fa-solid fa-clapperboard"
    name = "Media Type"
    name_plural = "Media Types"
    category = "Movie Directory"


class PersonsAdmin(ModelView, model=PersonsModel):
    column_list = [
        PersonsModel.id,
        PersonsModel.full_name,
        PersonsModel.birth_date,
    ]
    column_searchable_list = [PersonsModel.full_name]
    form_excluded_columns = [PersonsModel.movie_persons]
    icon = "fa-solid fa-user-tie"
    name = "Person"
    name_plural = "Persons"
    category = "Movie Directory"


class ProfessionsAdmin(ModelView, model=ProfessionsModel):
    column_list = [ProfessionsModel.id, ProfessionsModel.name]
    column_searchable_list = [ProfessionsModel.name]
    form_excluded_columns = [ProfessionsModel.movie_persons]
    icon = "fa-solid fa-briefcase"
    name = "Profession"
    name_plural = "Professions"
    category = "Movie Directory"


class MoviePersonsAdmin(ModelView, model=MoviePersonsModel):
    column_list = [
        MoviePersonsModel.id,
        MoviePersonsModel.movie,
        MoviePersonsModel.person,
        MoviePersonsModel.profession,
        MoviePersonsModel.character_name,
    ]
    column_searchable_list = [
        "movie.title",
        "movie.original_title",
        "person.full_name",
        "character_name",
    ]
    column_filters = [MoviePersonsModel.profession_id]
    form_ajax_refs = {
        "movie": {
            "fields": ("title", "original_title"),
        },
        "person": {
            "fields": ("full_name",),
        },
        "profession": {
            "fields": ("name",),
        },
    }
    icon = "fa-solid fa-users-rectangle"
    name = "Movie Cast/Crew"
    name_plural = "Movie Cast & Crew"
    category = "Movie Directory"


class PersonSubscriptionAdmin(ModelView, model=PersonSubscriptionModel):
    column_list = [
        PersonSubscriptionModel.id,
        PersonSubscriptionModel.user_id,
        PersonSubscriptionModel.person_id,
    ]
    column_filters = [
        PersonSubscriptionModel.user_id,
        PersonSubscriptionModel.person_id,
    ]
    icon = "fa-solid fa-bell"
    name = "Person Subscription"
    name_plural = "Person Subscriptions"
    category = "User Activity"


class MovieBookmarkAdmin(ModelView, model=MovieBookmarkModel):
    column_list = [
        MovieBookmarkModel.id,
        MovieBookmarkModel.user_id,
        MovieBookmarkModel.movie_id,
    ]
    column_filters = [MovieBookmarkModel.user_id, MovieBookmarkModel.movie_id]
    icon = "fa-solid fa-bookmark"
    name = "Movie Bookmark"
    name_plural = "Movie Bookmarks"
    category = "User Activity"


class NotificationAdmin(ModelView, model=NotificationModel):
    column_list = [
        NotificationModel.id,
        NotificationModel.user_id,
        NotificationModel.movie_id,
        NotificationModel.type,
        NotificationModel.status,
        NotificationModel.created_at,
    ]
    column_searchable_list = [NotificationModel.url_link]
    column_filters = [NotificationModel.type, NotificationModel.status]
    icon = "fa-solid fa-envelope"
    name = "Notification"
    name_plural = "Notifications"
    category = "Notifications"
