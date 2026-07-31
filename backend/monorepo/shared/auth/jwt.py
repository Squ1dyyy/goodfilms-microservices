from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

JWT_ALGORITHM = "HS256"


def create_access_token(
    secret_key: str,
    user_id: int,
    role: str,
    expires_in: int,
    is_verified: bool = False,
) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "is_verified": is_verified,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(
    token: str,
    secret_key: str,
) -> int:
    payload = jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
    sub = payload.get("sub")
    if not sub:
        raise JWTError("missing sub")
    return int(sub)


def decode_access_token_payload(
    token: str,
    secret_key: str,
) -> dict:
    return jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
