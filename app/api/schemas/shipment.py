from datetime import datetime

from pydantic import BaseModel, Field

from app.database.models import ShipmentStatus

class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)
    source: str
    destination: str

class ShipmentCreate(BaseShipment):
    pass

class ShipmentRead(BaseShipment):
    id: int
    status: ShipmentStatus
    estimated_delivery: datetime

class ShipmentUpdate(BaseModel):
    status: ShipmentStatus | None = None
    estimated_delivery: datetime | None = None
