from random import randint

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_url_safe_token
from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.database.redis import add_verification_code
from app.services.base import BaseService
from app.services.notification import NotificationService
from app.config import app_settings


class ShipmentEventService(BaseService):
    def __init__(self, session: AsyncSession, tasks: BackgroundTasks):
        super().__init__(session, ShipmentEvent)
        self.notification_service = NotificationService(tasks)

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

        await self._notify(shipment, status)
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

    async def _notify(self, shipment: Shipment, status: ShipmentStatus):
        if status == ShipmentStatus.in_transit:
            return

        recepients = [shipment.client_contact_email]
        subject: str = ""
        context = {
            "shipment": shipment.model_dump(),
            "seller": shipment.seller.name,
            "customer": shipment.client_contact_email,
            "delivery_partner": shipment.delivery_partner.name,
        }
        template_name: str = ""

        match status:
            case ShipmentStatus.placed:
                subject = "Order Confirmed 🎉"
                template_name = "placed.html"

            case ShipmentStatus.out_for_delivery:
                subject = "Your Order Is Out for Delivery 🚚"
                template_name = "out_for_delivery.html"
                code = randint(100_000, 999_999)
                context["verification_code"] = str(code)
                await add_verification_code(shipment.id, code)

            case ShipmentStatus.cancelled:
                subject = "Order Cancelled"
                template_name = "cancelled.html"

            case ShipmentStatus.delivered:
                subject = "Order Delivered ✅"
                template_name = "delivered.html"
                token = generate_url_safe_token({"id": str(shipment.id)})
                context["review_url"] = (
                    f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}"
                )

        await self.notification_service.send_email_with_template(
            recipients=recepients,
            subject=subject,
            template_name=template_name,
            context=context,
        )
