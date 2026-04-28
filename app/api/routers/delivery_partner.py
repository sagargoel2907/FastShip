from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.database.redis import add_jti_to_blacklist

from ..dependencies import (
    DeliveryPartnerDep,
    DeliveryPartnerServiceDep,
    get_delivery_partner_access_token_data,
)
from ..schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerRead,
    DeliveryPartnerUpdate,
)

router = APIRouter(prefix="/delivery-partner", tags=["Delivery partner"])


@router.post("/register", response_model=DeliveryPartnerRead)
async def register_delivery_partner(
    delivery_partner: DeliveryPartnerCreate, service: DeliveryPartnerServiceDep
):
    return await service.create(delivery_partner)


@router.get("/dashboard")
async def dashboard(delivery_partner: DeliveryPartnerDep):
    return delivery_partner


@router.get("/{id}", response_model=DeliveryPartnerRead)
async def get_delivery_partner(id: UUID, service: DeliveryPartnerServiceDep):
    return await service.get(id)


@router.post("/token")
async def token(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: DeliveryPartnerServiceDep,
):
    token = await service.get_access_token(request_form.username, request_form.password)

    return {"access_token": token, "type": "jwt"}


@router.post("/logout")
async def logout(
    token_data: Annotated[dict, Depends(get_delivery_partner_access_token_data)],
):
    await add_jti_to_blacklist(token_data["jti"])
    return {"details": "Successfully logged out!"}


@router.patch("/", response_model=DeliveryPartnerRead)
async def update_delivery_partner(
    delivery_partner: DeliveryPartnerUpdate,
    current_partner: DeliveryPartnerDep,
    service: DeliveryPartnerServiceDep,
):
    current_partner.sqlmodel_update(delivery_partner.model_dump(exclude_unset=True))
    return await service.update(current_partner)


@router.get("/", response_model=list[DeliveryPartnerRead])
async def get_all_delivery_partner(service: DeliveryPartnerServiceDep):
    return await service.get_all_delivery_partner()
