from pathlib import Path
from pydantic_settings import SettingsConfigDict

from monorepo.shared.config.base import BaseServiceConfig

_HERE = Path(__file__).parent


class Config(BaseServiceConfig):
    model_config = SettingsConfigDict(env_file=_HERE / ".env", extra="ignore")

    email_login: str
    email_password: str
    smtp_host: str = "sandbox.smtp.mailtrap.io"
    smtp_port: int = 587


config = Config()
