from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status

from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from app.api.schemas.shipment_review import ShipmentReviewCreate
from app.core.security import decode_url_safe_token
from app.database.models import (
    Seller,
    Shipment,
    ShipmentReview,
    ShipmentStatus,
    TagName,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.redis import get_verification_code
from app.services.delivery_partner import DeliveryPartnerService
from app.services.shipment_event import ShipmentEventService

from .base import BaseService


class ShipmentService(BaseService[Shipment]):
    def __init__(
        self,
        session: AsyncSession,
        delivery_partner_service: DeliveryPartnerService,
        shipment_event_service: ShipmentEventService,
    ):
        super().__init__(session, Shipment)
        self.delivery_partner_service = delivery_partner_service
        self.shipment_event_service = shipment_event_service

    async def get(
        self,
        id: UUID,
    ) -> Shipment | None:
        return await self._get(id)

    async def create(
        self,
        shipment: ShipmentCreate,
        seller: Seller,
    ) -> Shipment:
        new_shipment = Shipment(**shipment.model_dump(), seller_id=seller.id)
        partner = await self.delivery_partner_service.assign_shipment(new_shipment)
        new_shipment.delivery_partner = partner

        await self._create(new_shipment)

        await self.shipment_event_service.create(
            shipment=new_shipment,
            location=seller.zipcode,
            status=ShipmentStatus.placed,
            description=f"assigned delivery partner: {partner.name}",
        )
        await self._refresh(new_shipment)
        return new_shipment

    async def update(
        self,
        shipment: ShipmentUpdate,
        id: UUID,
    ) -> Shipment | None:
        db_shipment = await self.get(id)

        if not db_shipment:
            raise Exception()

        if shipment.estimated_delivery:
            db_shipment.estimated_delivery = shipment.estimated_delivery

        shipment_data = shipment.model_dump(exclude_unset=True)
        if not shipment_data:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="No shipment update provided",
            )
        if shipment.status == ShipmentStatus.delivered:
            code = await get_verification_code(db_shipment.id)
            if shipment.verification_code != code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"{type(code)} : {shipment.verification_code}",
                )

        if len(shipment_data) > 1 or not shipment.estimated_delivery:
            await self.shipment_event_service.create(
                shipment=db_shipment,
                location=shipment.location,
                status=shipment.status,
                description=shipment.description,
            )
        return await self._update(db_shipment)

    async def cancel(self, id: UUID, seller: Seller) -> Shipment:
        shipment = await self.get(id)
        if not shipment or shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment does not exist or seller mismatch",
            )

        event = await self.shipment_event_service.create(
            shipment=shipment,
            status=ShipmentStatus.cancelled,
        )

        shipment.timeline.append(event)
        return shipment

    async def get_all_shipments(
        self,
    ) -> Sequence[Shipment]:
        return await self._get_all()

    async def rate(self, review: ShipmentReviewCreate, token: str):
        token_data = decode_url_safe_token(token)
        if not token_data:
            raise HTTPException(
                detail="Invalid token", status_code=status.HTTP_400_BAD_REQUEST
            )
        shipment = await self.get(UUID(token_data["id"]))
        if not shipment:
            return
        new_review = ShipmentReview(**review.model_dump(), shipment_id=shipment.id)
        self.session.add(new_review)
        await self.session.commit()

    async def add_tag(self, id: UUID, tag: TagName):
        shipment = await self.get(id)
        if not shipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shipment does not exists"
            )

        tag_obj = await tag.get_tag(self.session)
        if not tag_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provided tag {tag.value} is invalid",
            )
        if tag_obj in shipment.tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag {tag.value} already exists on the shipment",
            )
        shipment.tags.append(tag_obj)
        await self._update(shipment)
        return shipment

    async def remove_tag(self, id: UUID, tag: TagName):
        shipment = await self.get(id)
        if not shipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shipment does not exists"
            )

        tag_obj = await tag.get_tag(self.session)
        if not tag_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provided tag {tag.value} is invalid",
            )

        try:
            shipment.tags.remove(tag_obj)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provided tag {tag.value} does not exist on the shipment",
            )
        await self._update(shipment)
        return shipment

    async def get_shipment_by_tag(self, tag: TagName):
        tag_obj = await tag.get_tag(session=self.session)
        if not tag_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid tag')
        
        return tag_obj.shipments