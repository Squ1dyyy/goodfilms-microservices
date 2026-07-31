from typing import Optional

from monorepo.shared.repository.redis_repository import BaseRedisRepository


class ResetTokenRedisRepository(BaseRedisRepository):
    _RESET_PREFIX = "forgot_token:"

    async def save_reset_token(
        self,
        hashed_token: str,
        user_id: int,
        ttl: int,
    ) -> None:
        await self.set(f"{self._RESET_PREFIX}{hashed_token}", str(user_id), ttl=ttl)

    async def get_reset_token(self, hashed_token: str) -> Optional[str]:
        return await self.get(f"{self._RESET_PREFIX}{hashed_token}")

    async def delete_reset_token(self, hashed_token: str) -> None:
        await self.delete(f"{self._RESET_PREFIX}{hashed_token}")
