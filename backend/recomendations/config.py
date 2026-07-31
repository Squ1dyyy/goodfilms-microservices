from pathlib import Path
from pydantic_settings import SettingsConfigDict

from monorepo.shared.config.base import BaseServiceConfig

_HERE = Path(__file__).parent


class Config(BaseServiceConfig):
    model_config = SettingsConfigDict(env_file=_HERE / ".env", extra="ignore")

    MOVIE_SERVICE_URL: str = "http://localhost:8002"


config = Config()
