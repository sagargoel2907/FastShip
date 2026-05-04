from datetime import datetime, timedelta
from enum import Enum

from sqlmodel import Relationship, SQLModel, Field, Column
from pydantic import EmailStr
from uuid import UUID, uuid4
from sqlalchemy.dialects import postgresql
from sqlalchemy import ARRAY, INTEGER


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"  # type: ignore

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )
    content: str
    weight: float = Field(le=25)
    source: str
    destination: str
    zipcode: int
    estimated_delivery: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(3)
    )
    seller_id: UUID = Field(foreign_key="seller.id")
    seller: "Seller" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    delivery_partner_id: UUID = Field(foreign_key="delivery_partner.id", nullable=True)
    delivery_partner: "DeliveryPartner" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    timeline: list["ShipmentEvent"] = Relationship(
        back_populates="shipment",
        sa_relationship_kwargs={
            "lazy": "selectin",
        },
    )

    client_contact_email: EmailStr
    client_contact_phone: str | None

    @property
    def status(self) -> ShipmentStatus:
        return max(self.timeline, key=lambda event: event.created_at).status


class User(SQLModel):
    name: str = Field(max_length=20)
    email: EmailStr = Field()
    password_hash: str


class Seller(User, table=True):
    __tablename__ = "seller"  # type: ignore
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    address: str | None = Field(default=None)
    zipcode: int | None = Field(default=None)

    shipments: list[Shipment] = Relationship(
        back_populates="seller",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partner"  # type: ignore
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    serviceable_zip_codes: list[int] = Field(
        sa_column=Column(ARRAY(INTEGER)),
    )
    max_handling_capacity: int

    shipments: list[Shipment] = Relationship(
        back_populates="delivery_partner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    @property
    def active_shipments(self):
        return [
            shipment
            for shipment in self.shipments
            if shipment.status != ShipmentStatus.delivered
        ]

    @property
    def current_handling_capacity(self):
        return self.max_handling_capacity - len(self.active_shipments)


class ShipmentEvent(SQLModel, table=True):
    __tablename__ = "shipment_event"  # type: ignore

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    location: int
    status: ShipmentStatus
    description: str | None = Field(default=None)

    shipment_id: UUID = Field(foreign_key="shipment.id")
    shipment: Shipment = Relationship(
        back_populates="timeline",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
