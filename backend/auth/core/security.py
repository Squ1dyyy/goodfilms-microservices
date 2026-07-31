import hashlib
import secrets
from typing import Optional, Tuple

import bcrypt

from auth.config import config
from auth.models.items import SessionModel
from monorepo.shared.auth.jwt import (
    create_access_token as _create_access_token,
    decode_access_token as _decode_access_token,
    decode_access_token_payload as _decode_access_token_payload,
)


def _encode(
    password: str,
) -> bytes:
    return password.encode("utf-8")


def hash_password(
    password: str,
) -> str:
    return bcrypt.hashpw(_encode(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    try:
        return bcrypt.checkpw(_encode(password), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(
    user_id: int,
    role: str,
    expires_in: Optional[int] = None,
    is_verified: bool = False,
) -> str:
    expires_in = expires_in or config.JWT_ACCESS_TOKEN_EXPIRE
    return _create_access_token(
        config.JWT_SECRET_KEY,
        user_id,
        role,
        expires_in,
        is_verified=is_verified,
    )


def decode_access_token(
    token: str,
) -> int:
    return _decode_access_token(token, config.JWT_SECRET_KEY)


def decode_access_token_payload(
    token: str,
) -> dict:
    return _decode_access_token_payload(token, config.JWT_SECRET_KEY)


def hash_session_token(
    token: str,
) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_session_data(
    user_id: int,
    client_info: dict,
) -> Tuple[str, SessionModel]:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_session_token(raw_token)

    session_model = SessionModel(
        user_id=user_id,
        token_hash=token_hash,
        device_name=client_info.get("device_name"),
        device_type=client_info.get("device_type"),
        user_agent=client_info.get("user_agent"),
        ip_address=client_info.get("ip_address"),
        country=client_info.get("country"),
    )

    return raw_token, session_model


def encode_sha256(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def create_sha256_token() -> tuple[str, str]:
    raw_token = secrets.token_urlsafe(32)
    hashed_token = encode_sha256(raw_token)
    return raw_token, hashed_token


def create_code() -> tuple[int, str]:
    code = secrets.randbelow(1_000_000)
    hashed_code = encode_sha256(str(code))
    return code, hashed_code
