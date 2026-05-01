from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.services.base import BaseService


class ShipmentEventService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ShipmentEvent)

    async def create(
        self,
        shipment: Shipment,
        location: int | None = None,
        status: ShipmentStatus | None = None,
        description: str | None = None,
    ) -> ShipmentEvent:

        if not location or not status:
            latest_event = self._get_latest_event_for_shipment(shipment)
            location = location if location else latest_event.location
            status = status if status else latest_event.status

        shipment_event = ShipmentEvent(
            location=location,
            status=status,
            description=description
            if description
            else self._get_shipment_description(status, location),
            shipment_id=shipment.id,
        )

        return await self._create(shipment_event)

    def _get_latest_event_for_shipment(self, shipment: Shipment) -> ShipmentEvent:
        return max(shipment.timeline, key=lambda event: event.created_at)

    def _get_shipment_description(self, status: ShipmentStatus, location: int) -> str:
        match status:
            case ShipmentStatus.placed:
                return "assigned delivery partner"
            case ShipmentStatus.out_for_delivery:
                return "shipment out for delivery"
            case ShipmentStatus.delivered:
                return "successfully delivered"
            case ShipmentStatus.cancelled:
                return "shipment cancelled by seller"
            case _:
                return f"scanned at {location}"
