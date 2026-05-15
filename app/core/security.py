from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
import jwt
from app.config import security_settings
from uuid import uuid4

oauth_scheme_seller = OAuth2PasswordBearer(
    tokenUrl="/seller/token", scheme_name="Seller"
)
oauth_scheme_delivery_partner = OAuth2PasswordBearer(
    tokenUrl="/delivery-partner/token", scheme_name="Delivery partner"
)

serializer = URLSafeTimedSerializer(secret_key=security_settings.JWT_SECRET)


def generate_jwt_access_token(data: dict, expiry: timedelta = timedelta(days=1)):
    return jwt.encode(
        payload={
            **data,
            "exp": datetime.now(timezone.utc) + expiry,
            "jti": uuid4().hex,
        },
        key=security_settings.JWT_SECRET,
        algorithm=security_settings.JWT_ALGORITHM,
    )


def decode_jwt_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            key=security_settings.JWT_SECRET,
            algorithms=[security_settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None


def generate_url_safe_token(data: dict, salt: str | None = None) -> str:
    return serializer.dumps(obj=data, salt=salt)


def decode_url_safe_token(
    token: str, expiry: timedelta | None = None, salt: str | None = None
) -> dict | None:
    try:
        return serializer.loads(
            token, max_age=int(expiry.total_seconds()) if expiry else None, salt=salt
        )
    except (BadSignature, SignatureExpired):
        return None
