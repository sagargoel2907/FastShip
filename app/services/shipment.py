from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from app.database.models import Shipment

from sqlalchemy.ext.asyncio import AsyncSession

class ShipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Shipment | None:
        return await self.session.get(Shipment, id)

    async def create(self, shipment: ShipmentCreate) -> Shipment:
        db_shipment = Shipment.model_validate(shipment)
        self.session.add(db_shipment)
        await self.session.commit()
        await self.session.refresh(db_shipment)
        return db_shipment

    async def update(self, shipment: ShipmentUpdate, id: int) -> Shipment | None:
        db_shipment = await self.get(id)
        
        if not db_shipment:
            raise Exception()
        db_shipment.sqlmodel_update(shipment.model_dump(exclude_unset=True))
        self.session.add(db_shipment)
        await self.session.commit()
        await self.session.refresh(db_shipment)
        return db_shipment

    async def delete(self, id: int) -> None:
        await self.session.delete(await self.get(id))
        await self.session.commit()

        