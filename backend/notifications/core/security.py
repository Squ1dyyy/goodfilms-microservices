from notifications.config import config
from monorepo.shared.auth.jwt import decode_access_token as _decode_access_token


def decode_access_token(token: str) -> int:
    return _decode_access_token(token, config.JWT_SECRET_KEY)
