from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.api.schemas.seller import SellerRead
from app.api.schemas.shipment_event import ShipmentEventRead
from app.database.models import ShipmentStatus

class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)
    source: str
    destination: str
    zipcode: int

class ShipmentCreate(BaseShipment):
    pass

class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEventRead]
    estimated_delivery: datetime
    seller: SellerRead

class ShipmentUpdate(BaseModel):
    status: ShipmentStatus | None = None
    estimated_delivery: datetime | None = None
    location: int | None = None
    description: str | None = None
