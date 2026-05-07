from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.api.schemas.seller import SellerRead
from app.api.schemas.shipment_event import ShipmentEventRead
from app.database.models import ShipmentStatus, TagName


class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)
    source: str
    destination: str
    zipcode: int
    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)


class ShipmentCreate(BaseShipment):
    pass

class TagRead(BaseModel):
    name: TagName
    description: str
class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEventRead]
    estimated_delivery: datetime
    seller: SellerRead
    tags: list[TagRead]


class ShipmentUpdate(BaseModel):
    status: ShipmentStatus | None = None
    estimated_delivery: datetime | None = None
    location: int | None = None
    description: str | None = None
    verification_code: str | None = None
