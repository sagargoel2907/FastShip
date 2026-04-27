from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
import jwt
from app.config import security_settings
from uuid import uuid4

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/seller/token")


def generate_jwt_token(data: dict, expiry: timedelta = timedelta(days=1)):
    return jwt.encode(
        payload={
            **data,
            "exp": datetime.now(timezone.utc) + expiry,
            "jti": uuid4().hex,
        },
        key=security_settings.JWT_SECRET,
        algorithm=security_settings.JWT_ALGORITHM,
    )

def decode_jwt_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, key=security_settings.JWT_SECRET, algorithms=[security_settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None