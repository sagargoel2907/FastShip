from datetime import datetime, timedelta
from enum import Enum

from sqlmodel import Relationship, SQLModel, Field, Column, select
from pydantic import EmailStr
from uuid import UUID, uuid4
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class TagName(str, Enum):
    express = "express"
    same_day = "same_day"
    priority = "priority"
    fragile = "fragile"
    handle_with_care = "handle_with_care"
    keep_upright = "keep_upright"
    temperature_controlled = "temperature_controlled"
    perishable = "perishable"
    high_value = "high_value"
    insured = "insured"
    signature_required = "signature_required"
    hazardous = "hazardous"
    flammable = "flammable"
    medical = "medical"
    pharmaceutical = "pharmaceutical"
    gift = "gift"

    async def get_tag(self, session: AsyncSession):
        return await session.scalar(select(Tag).where(Tag.name == self.value))


class ShipmentTag(SQLModel, table=True):
    shipment_id: UUID = Field(foreign_key="shipment.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tag.id", primary_key=True)


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

    review: "ShipmentReview" = Relationship(
        back_populates="shipment",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    tags: list["Tag"] = Relationship(
        back_populates="shipments",
        link_model=ShipmentTag,
        sa_relationship_kwargs={"lazy": "immediate"},
    )

    @property
    def status(self) -> ShipmentStatus:
        return max(self.timeline, key=lambda event: event.created_at).status


class Tag(SQLModel, table=True):
    __tablename__ = "tag"  # type: ignore
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
    name: TagName
    description: str
    shipments: list[Shipment] = Relationship(
        back_populates="tags",
        link_model=ShipmentTag,
        sa_relationship_kwargs={"lazy": "immediate"},
    )


class User(SQLModel):
    name: str = Field(max_length=20)
    email: EmailStr = Field(unique=True)
    password_hash: str
    email_verified: bool = Field(default=False)


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


class ServiceableLocation(SQLModel, table=True):
    __tablename__ = "serviceable_location"  # type: ignore
    delivery_partner_id: UUID = Field(
        foreign_key="delivery_partner.id", primary_key=True
    )
    location_id: int = Field(foreign_key="location.zip_code", primary_key=True)


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

    serviceable_locations: list["Location"] = Relationship(
        back_populates="delivery_partners",
        sa_relationship_kwargs={"lazy": "selectin"},
        link_model=ServiceableLocation,
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


class Location(SQLModel, table=True):
    __tablename__ = "location" # type: ignore
    zip_code: int = Field(primary_key=True)
    delivery_partners: list[DeliveryPartner] = Relationship(
        back_populates="serviceable_locations",
        sa_relationship_kwargs={"lazy": "selectin"},
        link_model=ServiceableLocation,
    )


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


class ShipmentReview(SQLModel, table=True):
    __tablename__ = "shipment_review"  # type: ignore
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

    rating: int = Field(ge=1, le=5)
    comment: str | None

    shipment_id: UUID = Field(foreign_key="shipment.id")
    shipment: Shipment = Relationship(
        back_populates="review",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
