from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
import jwt
from app.config import security_settings
from uuid import uuid4

oauth_scheme_seller = OAuth2PasswordBearer(tokenUrl="/seller/token")
oauth_scheme_delivery_partner = OAuth2PasswordBearer(tokenUrl="/delivery-partner/token")

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
        return jwt.decode(token, key=security_settings.JWT_SECRET, algorithms=[security_settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    
def generate_url_safe_token(data:dict) -> str:
    return serializer.dumps(obj=data)

def decode_url_safe_token(token: str) -> dict | None:
    try:
        return serializer.loads(token, max_age=int(timedelta(days=1).total_seconds()))
    except (BadSignature, SignatureExpired):
        return None
