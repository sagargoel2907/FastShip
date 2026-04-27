from datetime import datetime, timedelta
from enum import Enum

from sqlmodel import Relationship, SQLModel, Field, Column
from pydantic import EmailStr
from uuid import UUID, uuid4
from sqlalchemy.dialects import postgresql


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"  # type: ignore

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    content: str
    weight: float = Field(le=25)
    source: str
    destination: str
    status: ShipmentStatus = Field(default=ShipmentStatus.placed)
    estimated_delivery: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(3)
    )
    seller_id: UUID = Field(foreign_key="seller.id")
    seller: "Seller" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Seller(SQLModel, table=True):
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    name: str = Field(max_length=20)
    email: EmailStr
    password_hash: str
    shipments: list[Shipment] = Relationship(
        back_populates="seller", sa_relationship_kwargs={"lazy": "selectin"}
    )
