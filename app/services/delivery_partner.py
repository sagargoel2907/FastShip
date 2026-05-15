from typing import Sequence
from uuid import UUID

from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy import any_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.delivery_partner import DeliveryPartnerCreate
from app.core.exceptions import DeliveryPartnerNotAvailableException
from app.database.models import DeliveryPartner, Location, Shipment
from app.services.user import UserService

password_context = CryptContext(schemes=["argon2"], deprecated="auto")


class DeliveryPartnerService(UserService[DeliveryPartner]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DeliveryPartner)

    async def create(self, delivery_partner: DeliveryPartnerCreate) -> DeliveryPartner:
        db_partner = await self._create_user(
            delivery_partner.model_dump(), router_prefix="delivery-partner"
        )
        for zip_code in delivery_partner.serviceable_zip_codes:
            location = await self.session.get(Location, zip_code)
            db_partner.serviceable_locations.append(
                location if location else Location(zip_code=zip_code)
            )
            await self.update(db_partner)
        return db_partner

    async def get(self, id: UUID) -> DeliveryPartner | None:
        return await self._get(id)

    async def get_access_token(self, email: EmailStr, password: str) -> str:
        return await self._get_access_token(email, password)

    async def get_all_delivery_partner(self) -> Sequence[DeliveryPartner]:
        return await self._get_all()

    async def update(self, delivery_partner: DeliveryPartner) -> DeliveryPartner:
        return await self._update(delivery_partner)

    async def get_available_partner_for_zipcode(
        self, zipcode: int
    ) -> Sequence[DeliveryPartner]:
        result = await self.session.scalars(
            select(DeliveryPartner)
            .join(DeliveryPartner.serviceable_locations)
            .where(Location.zip_code == zipcode)
        )
        return result.all()

    async def assign_shipment(self, shipment: Shipment):
        eligible_partners = await self.get_available_partner_for_zipcode(
            shipment.zipcode
        )
        for partner in eligible_partners:
            if partner.current_handling_capacity > 0:
                return partner

        raise DeliveryPartnerNotAvailableException()
