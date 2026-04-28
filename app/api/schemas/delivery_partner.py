from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

from app.api.schemas.shipment import ShipmentRead

class BaseDeliveryPartner(BaseModel):
    name: str = Field(max_length=20)
    email: EmailStr
    serviceable_zip_codes: list[int]
    max_handling_capacity: int

class DeliveryPartnerRead(BaseDeliveryPartner):
    id: UUID
    shipments: list[ShipmentRead]

class DeliveryPartnerCreate(BaseDeliveryPartner):
    password: str

class DeliveryPartnerUpdate(BaseModel):
    name: str | None = Field(max_length=20, default=None)
    email: EmailStr | None = Field(default=None)
    serviceable_zip_codes: list[int] | None = Field(default=None)
    max_handling_capacity: int | None = Field(default=None)
