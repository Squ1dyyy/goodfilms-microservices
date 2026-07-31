from pydantic_settings import BaseSettings


class BaseServiceConfig(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    RABBIT_BROKER_URL: str
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE: int = 60 * 15
    SESSION_EXPIRES_SECONDS: int = 60 * 60 * 24

    @property
    def SQL_ALCHEMY_DATABASE_URL(self) -> str:
        return self.DATABASE_URL
