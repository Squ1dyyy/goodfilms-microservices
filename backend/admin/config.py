from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_HERE = Path(__file__).parent


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=_HERE / ".env", extra="ignore")

    DATABASE_URL: str
    MOVIE_DATABASE_URL: str
    USERS_DATABASE_URL: str
    NOTIFICATIONS_DATABASE_URL: str
    JWT_SECRET_KEY: str


config = Config()
