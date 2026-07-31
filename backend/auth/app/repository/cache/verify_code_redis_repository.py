from typing import Optional

from monorepo.shared.repository.redis_repository import BaseRedisRepository


class VerifyCodeRedisRepository(BaseRedisRepository):
    _VERIFY_PREFIX = "verify_token:"

    async def save_verify_code(
        self,
        hashed_token: str,
        user_id: int,
        ttl: int,
    ) -> None:
        await self.set(f"{self._VERIFY_PREFIX}{hashed_token}", str(user_id), ttl=ttl)

    async def get_verify_code(self, hashed_token: str) -> Optional[str]:
        return await self.get(f"{self._VERIFY_PREFIX}{hashed_token}")

    async def delete_verify_code(self, hashed_token: str) -> None:
        await self.delete(f"{self._VERIFY_PREFIX}{hashed_token}")
