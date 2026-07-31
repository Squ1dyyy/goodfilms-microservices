from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.app.repository.cache.session_redis_repository import SessionRedisRepository
from auth.app.repository.cache.reset_token_redis_repository import (
    ResetTokenRedisRepository,
)
from auth.app.repository.cache.verify_code_redis_repository import (
    VerifyCodeRedisRepository,
)
from auth.app.schemas.session import SessionSchema
from auth.app.schemas.user import (
    LoginUserSchema,
    RegisterUserSchema,
    EditPasswordSchema,
)
from auth.app.repository.sql import user_repository, session_repository
from auth.models.items import UserModel

from auth.core import security
from auth.exception.exceptions import AlreadyExists, InvalidCredentials, NotFound
from auth.config import config


class AuthService:
    def __init__(
        self,
        session: Optional[AsyncSession] = None,
        session_redis: Optional[SessionRedisRepository] = None,
        reset_redis: Optional[ResetTokenRedisRepository] = None,
        verify_redis: Optional[VerifyCodeRedisRepository] = None,
    ):
        self.session = session
        self.session_redis = session_redis
        self.reset_redis = reset_redis
        self.verify_redis = verify_redis

    @property
    def db_session(self) -> AsyncSession:
        if self.session is None:
            raise RuntimeError("Database session is not initialized")
        return self.session

    @property
    def session_cache(self) -> SessionRedisRepository:
        if self.session_redis is None:
            raise RuntimeError("Session redis repository is not initialized")
        return self.session_redis

    @property
    def reset_cache(self) -> ResetTokenRedisRepository:
        if self.reset_redis is None:
            raise RuntimeError("Reset token redis repository is not initialized")
        return self.reset_redis

    @property
    def verify_cache(self) -> VerifyCodeRedisRepository:
        if self.verify_redis is None:
            raise RuntimeError("Verify code redis repository is not initialized")
        return self.verify_redis

    async def authenticate(
        self,
        data: LoginUserSchema,
        client_info: dict,
    ) -> tuple[UserModel, str]:
        user = await user_repository.get_by_email(self.db_session, data.email)

        if user is None or not security.verify_password(
            data.password,
            user.password_hash,
        ):
            raise InvalidCredentials("invalid email or password")

        raw_token, session_model = security.generate_session_data(user.id, client_info)

        user_agent = client_info.get("user_agent")
        if not isinstance(user_agent, str):
            user_agent = ""

        existing_sessions = await session_repository.get_sessions_by_user_agent(
            self.db_session,
            user.id,
            user_agent,
        )
        for s in existing_sessions:
            await self.session_cache.delete_session(s.token_hash)
            await self.db_session.delete(s)

        await session_repository.add_session(self.db_session, session_model)

        await self.db_session.flush()
        await self.session_cache.save_session(
            session_model.token_hash,
            user.id,
            ttl=config.SESSION_EXPIRES_SECONDS,
        )
        await self.db_session.commit()
        return user, raw_token

    async def register(
        self,
        data: RegisterUserSchema,
        client_info: dict,
    ) -> tuple[UserModel, str]:
        if data.password != data.password_confirm:
            raise InvalidCredentials("passwords do not match")
        existing_user = await user_repository.get_by_email(self.db_session, data.email)
        if existing_user is not None:
            raise AlreadyExists("email already registered")

        user = UserModel(
            email=data.email,
            username=data.username,
            password_hash=security.hash_password(data.password),
        )
        try:
            await user_repository.create_user(self.db_session, user)
            await self.db_session.flush()
        except IntegrityError as e:
            raise AlreadyExists("email already registered") from e

        raw_token, session_model = security.generate_session_data(user.id, client_info)
        await session_repository.add_session(self.db_session, session_model)
        await self.db_session.flush()
        await self.session_cache.save_session(
            session_model.token_hash,
            session_model.user_id,
            ttl=config.SESSION_EXPIRES_SECONDS,
        )
        await self.db_session.commit()
        return user, raw_token

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> tuple[UserModel, str]:
        token_hash = security.hash_session_token(refresh_token)
        user_id = await self.session_cache.get_session(token_hash)

        if user_id is None:
            raise InvalidCredentials("invalid or expired refresh token")

        user = await user_repository.get_by_id(self.db_session, int(user_id))
        if user is None:
            raise InvalidCredentials("user not found")

        return user, security.create_access_token(
            user.id, user.role, is_verified=user.is_verified
        )

    async def logout(self, refresh_token: str) -> None:
        session_token = security.hash_session_token(refresh_token)
        await self.session_cache.delete_session(session_token)
        await session_repository.delete_session_by_token(self.db_session, session_token)
        await self.db_session.commit()

    async def delete_session_by_id(
        self,
        session_id: int,
        user_id: int,
    ) -> None:
        session_model = await session_repository.get_session_by_id(
            self.db_session,
            session_id,
            user_id,
        )
        if session_model is None:
            raise NotFound("session not found")

        await self.session_cache.delete_session(session_model.token_hash)
        await self.db_session.delete(session_model)
        await self.db_session.commit()

    async def change_password(
        self,
        user: UserModel,
        data: EditPasswordSchema,
        client_info: dict,
    ) -> tuple[UserModel, str]:
        if not security.verify_password(data.current_password, user.password_hash):
            raise InvalidCredentials("wrong current password")
        if data.new_password != data.new_password_confirm:
            raise InvalidCredentials("passwords do not match")

        user_sessions = await session_repository.get_sessions(self.db_session, user.id)
        if user_sessions:
            await self.session_cache.delete_sessions(
                [s.token_hash for s in user_sessions]
            )
        await session_repository.delete_sessions(self.db_session, user.id)

        user.password_hash = security.hash_password(data.new_password)

        raw_token, session_model = security.generate_session_data(user.id, client_info)
        await session_repository.add_session(self.db_session, session_model)
        await self.db_session.flush()
        await self.session_cache.save_session(
            session_model.token_hash,
            user.id,
            ttl=config.SESSION_EXPIRES_SECONDS,
        )
        await self.db_session.commit()

        return user, raw_token

    async def delete_sessions(
        self,
        access_token: str,
    ) -> None:
        user_id = security.decode_access_token(access_token)

        user_sessions = await session_repository.get_sessions(self.db_session, user_id)
        if not user_sessions:
            raise NotFound()

        await self.session_cache.delete_sessions([s.token_hash for s in user_sessions])
        await session_repository.delete_sessions(self.db_session, user_id)
        await self.db_session.commit()

    async def reset_password(
        self,
        token: str,
        new_password: str,
    ) -> None:
        user_id = await self.verify_token(token)
        user = await user_repository.get_by_id(self.db_session, user_id)

        if user is None:
            raise NotFound()

        user.password_hash = security.hash_password(new_password)
        hashed_token = security.encode_sha256(token)
        await self.reset_cache.delete_reset_token(hashed_token)
        await self.db_session.commit()

    async def forgot_password(
        self,
        email: str,
    ) -> Optional[str]:
        user = await user_repository.get_by_email(self.db_session, email)
        if user is None:
            return None

        raw_token, hashed_token = security.create_sha256_token()
        await self.reset_cache.save_reset_token(hashed_token, user.id, ttl=900)
        return raw_token

    async def verify_email(
        self,
        code: int,
    ) -> None:
        hashed_code = security.encode_sha256(str(code))
        user_id = await self.verify_cache.get_verify_code(hashed_code)
        if user_id is None:
            raise InvalidCredentials()

        user = await user_repository.get_by_id(self.db_session, int(user_id))
        if user is None:
            raise NotFound()

        user.is_verified = True
        await self.verify_cache.delete_verify_code(hashed_code)
        await self.db_session.commit()
        return None

    async def get_sessions(
        self,
        data: UserModel,
    ) -> list[SessionSchema]:
        user_sessions = await session_repository.get_sessions(self.db_session, data.id)
        if user_sessions is None:
            return []
        return [SessionSchema.model_validate(s) for s in user_sessions]

    async def verify_token(self, token: str) -> int:
        """Only Redis"""
        hashed_token = security.encode_sha256(token)
        user_id = await self.reset_cache.get_reset_token(hashed_token)
        if user_id is None:
            raise InvalidCredentials()
        return int(user_id)

    async def send_verification(
        self,
        user_id: int,
    ) -> int:
        """Only Redis"""
        code, hashed_code = security.create_code()
        await self.verify_cache.save_verify_code(hashed_code, user_id, ttl=900)
        return code
