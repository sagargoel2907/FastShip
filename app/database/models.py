from datetime import datetime, timedelta
from enum import Enum

from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"  # type: ignore

    id: int = Field(primary_key=True, default=None)
    content: str
    weight: float = Field(le=25)
    source: str
    destination: str
    status: ShipmentStatus = Field(default=ShipmentStatus.placed)
    estimated_delivery: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(3)
    )


class Seller(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=20)
    email: EmailStr
    password_hash: str