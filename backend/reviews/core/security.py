from reviews.config import config
from monorepo.shared.auth.jwt import (
    decode_access_token as _decode_access_token,
    decode_access_token_payload as _decode_access_token_payload,
)


def decode_access_token(token: str) -> int:
    return _decode_access_token(token, config.JWT_SECRET_KEY)


def decode_access_token_payload(token: str) -> dict:
    return _decode_access_token_payload(token, config.JWT_SECRET_KEY)
