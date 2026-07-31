from typing import Optional

from monorepo.shared.repository.redis_repository import BaseRedisRepository


class SessionRedisRepository(BaseRedisRepository):
    _SESSION_PREFIX = "session:"

    async def save_session(
        self,
        token_hash: str,
        user_id: int,
        ttl: int,
    ) -> None:
        await self.set(f"{self._SESSION_PREFIX}{token_hash}", str(user_id), ttl=ttl)

    async def get_session(
        self,
        token_hash: str,
    ) -> Optional[str]:
        return await self.get(f"{self._SESSION_PREFIX}{token_hash}")

    async def delete_session(
        self,
        token_hash: str,
    ) -> None:
        await self.delete(f"{self._SESSION_PREFIX}{token_hash}")

    async def delete_sessions(self, token_hashes: list[str]) -> None:
        await self.delete([f"{self._SESSION_PREFIX}{h}" for h in token_hashes])
