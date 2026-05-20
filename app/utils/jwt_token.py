from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from config import jwt_settings


def generate_access_token(token: dict, time=10) -> str:
    payload = token.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=time)

    payload.update({"exp": expire})

    return jwt.encode(
        claims=payload, key=jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM
    )


def verify_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token=token,
            key=jwt_settings.SECRET_KEY,
            algorithms=[jwt_settings.ALGORITHM],
        )
    except JWTError:
        return None
