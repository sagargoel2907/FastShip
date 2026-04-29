from datetime import timedelta

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select

from app.core.security import generate_jwt_token
from app.database.models import DeliveryPartner, Seller
from app.services.base import BaseService

from typing import TypeVar
from passlib.context import CryptContext

password_context = CryptContext(schemes=["argon2"], deprecated="auto")

UserT = TypeVar('UserT', Seller, DeliveryPartner)

class UserService(BaseService[UserT]):
    async def _get_access_token(self, email: EmailStr, password: str) -> str:
        user = await self.session.scalar(select(self.model).where(self.model.email == email))
        if not user or not password_context.verify(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect",
            )

        token = generate_jwt_token(data={
            'user':{
                'name': user.name,
                'id': str(user.id),
            }
        }, expiry=timedelta(hours=2))

        return token