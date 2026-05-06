from datetime import timedelta
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    decode_url_safe_token,
    generate_jwt_access_token,
    generate_url_safe_token,
)
from app.database.models import DeliveryPartner, Seller
from app.services.base import BaseService

from typing import TypeVar
from passlib.context import CryptContext

from app.config import app_settings
from app.worker.task import send_email_with_template

password_context = CryptContext(schemes=["argon2"], deprecated="auto")

UserT = TypeVar("UserT", Seller, DeliveryPartner)


class UserService(BaseService[UserT]):
    def __init__(
        self, session: AsyncSession, model: type[UserT]
    ):
        super().__init__(session, model)

    async def _get_user_by_email(self, email: EmailStr):
        user = await self.session.scalar(
            select(self.model).where(self.model.email == email)
        )
        return user

    async def _get_access_token(self, email: EmailStr, password: str) -> str:
        user = await self.session.scalar(
            select(self.model).where(self.model.email == email)
        )
        if not user or not password_context.verify(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect",
            )

        token = generate_jwt_access_token(
            data={
                "user": {
                    "name": user.name,
                    "id": str(user.id),
                }
            },
            expiry=timedelta(hours=2),
        )

        return token

    async def _create_user(self, data: dict, router_prefix: str) -> UserT:
        user = self.model(**data, password_hash=password_context.hash(data["password"]))
        await self._create(user)

        token = generate_url_safe_token({"email": user.email, "id": str(user.id)})
        send_email_with_template.delay( # type: ignore
            recipients=[user.email],
            subject="Verify your email for FastShip",
            template_name="verify_email.html",
            context={
                "username": user.name,
                "verification_link": f"http://{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}",
            },
        )
        return user

    async def verify_user_email_with_token(self, token: str):
        token_data = decode_url_safe_token(token=token, expiry=timedelta(days=1))
        if not token_data:
            raise HTTPException(
                detail="Invalid token", status_code=status.HTTP_400_BAD_REQUEST
            )
        user = await self._get(UUID(token_data["id"]))
        if not user:
            raise HTTPException(
                detail="Invalid token", status_code=status.HTTP_400_BAD_REQUEST
            )
        user.email_verified = True
        await self._update(user)

    async def send_password_reset_email(self, email: EmailStr, router_prefix: str):
        user = await self._get_user_by_email(email)
        if not user:
            return
        token = generate_url_safe_token(
            {"email": user.email, "id": str(user.id)}, salt="forgot-password"
        )
        send_email_with_template.delay( # type: ignore
            recipients=[email],
            subject="FastShip Account Password reset",
            context={
                "username": user.name,
                "reset_password_link": f"http://{app_settings.APP_DOMAIN}{router_prefix}/reset-password-form?token={token}",
            },
            template_name="forgot_password.html",
        )

    async def reset_password(self, token: str, password: str):
        token_data = decode_url_safe_token(
            token, expiry=timedelta(days=1), salt="forgot-password"
        )
        if not token_data:
            return False
        user = await self._get(UUID(token_data["id"]))
        if not user:
            return False
        user.password_hash = password_context.hash(password)
        await self._update(user)
        return True
