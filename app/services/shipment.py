from typing import Sequence
from uuid import UUID

from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from app.database.models import Seller, Shipment

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.delivery_partner import DeliveryPartnerService

from .base import BaseService

class ShipmentService(BaseService[Shipment]):
    def __init__(self, session: AsyncSession, delivery_partner_service: DeliveryPartnerService):
        super().__init__(session, Shipment)
        self.delivery_partner_service = delivery_partner_service

    async def get(self, id: UUID) -> Shipment | None:
        return await self._get(id)

    async def create(self, shipment: ShipmentCreate, seller: Seller) -> Shipment:
        db_shipment = Shipment(**shipment.model_dump(), seller_id = seller.id)
        await self.delivery_partner_service.assign_shipment(db_shipment)
        return await self._create(db_shipment)

    async def update(self, shipment: ShipmentUpdate, id: UUID) -> Shipment | None:
        db_shipment = await self.get(id)

        if not db_shipment:
            raise Exception()
        db_shipment.sqlmodel_update(shipment.model_dump(exclude_unset=True))
        return await self._update(db_shipment)

    async def delete(self, id: UUID) -> None:
        await self._delete(id)

    async def get_all_shipments(self) -> Sequence[Shipment]:
        return await self._get_all()