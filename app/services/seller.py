from datetime import timedelta

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.schemas.seller import SellerCreate
from app.core.security import generate_jwt_token
from app.database.models import Seller
from passlib.context import CryptContext

password_context = CryptContext(schemes=["argon2"], deprecated="auto")


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, seller: SellerCreate) -> Seller:
        db_seller = Seller(
            **seller.model_dump(exclude=set(["password"])),
            password_hash=password_context.hash(seller.password),
        )
        self.session.add(db_seller)
        await self.session.commit()
        await self.session.refresh(db_seller)
        return db_seller

    async def get(self, id: int) -> Seller | None:
        return await self.session.get(Seller, id)

    async def get_access_token(self, email: EmailStr, password: str) -> str:
        seller = await self.session.scalar(select(Seller).where(Seller.email == email))
        if not seller or not password_context.verify(password, seller.password_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect",
            )

        token = generate_jwt_token(data={
            'user':{
                'name': seller.name,
                'id': seller.id,
            }
        }, expiry=timedelta(hours=2))

        return token
