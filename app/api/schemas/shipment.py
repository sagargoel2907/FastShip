from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.database.models import Seller, ShipmentStatus

class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)
    source: str
    destination: str

class ShipmentCreate(BaseShipment):
    pass

class ShipmentRead(BaseShipment):
    id: UUID
    status: ShipmentStatus
    estimated_delivery: datetime
    seller: Seller

class ShipmentUpdate(BaseModel):
    status: ShipmentStatus | None = None
    estimated_delivery: datetime | None = None
