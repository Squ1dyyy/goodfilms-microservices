from datetime import timedelta
from typing import Optional, Union, TypeVar, Generic
from pydantic import BaseModel

from redis.asyncio import Redis


class BaseRedisRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[Union[int, timedelta]] = None,
    ):
        ex_seconds = None
        if ttl is not None:
            if isinstance(ttl, timedelta):
                ex_seconds = int(ttl.total_seconds())
            else:
                ex_seconds = int(ttl)
        await self.redis.set(key, value, ex=ex_seconds)

    async def delete(
        self,
        key: Union[str, list[str]],
    ):
        if isinstance(key, list):
            await self.redis.delete(*key)
        else:
            await self.redis.delete(key)


T = TypeVar("T", bound=BaseModel)


class GenericRedisRepository(BaseRedisRepository, Generic[T]):
    prefix: str = ""
    model_class: type[T] = None

    def _get_key(self, id: Union[int, str]) -> str:
        return f"{self.prefix}{id}"

    async def save_entity(
        self, id: Union[int, str], data: T, ttl: Optional[int] = None
    ) -> None:
        await self.set(self._get_key(id), data.model_dump_json(), ttl=ttl)

    async def get_entity(self, id: Union[int, str]) -> Optional[T]:
        raw = await self.get(self._get_key(id))
        if raw is None:
            return None
        return self.model_class.model_validate_json(raw)

    async def delete_entity(self, id: Union[int, str]) -> None:
        await self.delete(self._get_key(id))
