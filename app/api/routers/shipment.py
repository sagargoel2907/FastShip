from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from app.api.schemas.shipment_review import ShipmentReviewCreate
from app.config import TEMPLATES_FOLDER, app_settings
from app.database.models import TagName

from ..dependencies import (
    DeliveryPartnerDep,
    SellerDep,
    ShipmentServiceDep,
)
from ..schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate

templates = Jinja2Templates(directory=TEMPLATES_FOLDER)

router = APIRouter(prefix="/shipment", tags=["Shipment"], dependencies=[])  # type: ignore




@router.post("/", response_model=ShipmentRead)
async def create_shipment(
    seller: SellerDep,
    shipment: ShipmentCreate,
    service: ShipmentServiceDep,
):
    db_shipment = await service.create(shipment, seller)
    return db_shipment


@router.patch("/{id}", response_model=ShipmentRead)
async def update_shipment(
    shipment: ShipmentUpdate,
    id: UUID,
    service: ShipmentServiceDep,
    delivery_partner: DeliveryPartnerDep,
):
    db_shipment = await service.update(shipment, id)
    if not db_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment does not exists"
        )
    return db_shipment


@router.post("/cancel/{id}", response_model=ShipmentRead)
async def cancel_shipment(
    id: UUID,
    service: ShipmentServiceDep,
    seller: SellerDep,
):
    return await service.cancel(id, seller)


@router.get("/", response_model=list[ShipmentRead])
async def get_all_shipments(
    service: ShipmentServiceDep,
):
    return await service.get_all_shipments()


@router.get("/track/{id}")
async def track_shipment_page(request: Request, id: UUID, service: ShipmentServiceDep):
    shipment = await service.get(id)
    if not shipment:
        return templates.TemplateResponse(
            request=request, name="shipment_not_found.html"
        )
    context = {
        "shipment": shipment.model_dump(),
        "seller": shipment.seller.name,
        "delivery_partner": shipment.delivery_partner.name,
        "timeline": shipment.timeline,
        "status": shipment.status,
    }
    return templates.TemplateResponse(
        request=request, name="shipment_track.html", context=context
    )


@router.get("/review")
def review_form(request: Request, token: str):
    return templates.TemplateResponse(
        request=request,
        name="review_form.html",
        context={
            "review_url": f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}"
        },
    )


@router.post("/review")
async def review(
    token: str,
    review: Annotated[ShipmentReviewCreate, Form()],
    service: ShipmentServiceDep,
):
    await service.rate(review, token)
    return {"details": "Review submitted"}

@router.post('/tag', response_model=ShipmentRead)
async def add_tag(id: UUID, tag: TagName, service: ShipmentServiceDep):
    return await service.add_tag(id, tag)

@router.delete('/tag', response_model=ShipmentRead)
async def remove_tag(id: UUID, tag: TagName, service: ShipmentServiceDep):
    return await service.remove_tag(id, tag)

@router.get('/tagged', response_model=list[ShipmentRead])
async def get_shipment_by_tag(tag: TagName, service: ShipmentServiceDep):
    return await service.get_shipment_by_tag(tag)

@router.get("/{id}", response_model=ShipmentRead)
async def get_shipment(
    id: UUID,
    service: ShipmentServiceDep,
):
    shipment = await service.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment does not exists"
        )
    return shipment
