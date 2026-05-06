from typing import Sequence
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.seller import SellerCreate
from app.database.models import Seller

from app.services.user import UserService



class SellerService(UserService[Seller]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Seller)

    async def create(self, seller: SellerCreate) -> Seller:
        db_seller = await self._create_user(
            seller.model_dump(),
            router_prefix='seller'
        )
        return db_seller

    async def get(self, id: UUID) -> Seller | None:
        return await self._get(id)

    async def get_access_token(self, email: EmailStr, password: str) -> str:
        return await self._get_access_token(email, password)
    
    async def get_all_sellers(self) -> Sequence[Seller]:
        return await self._get_all()
