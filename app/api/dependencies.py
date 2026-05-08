from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.exceptions import EmailNotVerifiedException, EnitityNotFoundException, InvalidTokenException
from app.database.models import Seller, DeliveryPartner
from app.database.redis import is_jti_blacklisted
from app.database.session import get_session
from app.services.delivery_partner import DeliveryPartnerService
from app.services.seller import SellerService
from app.services.shipment import ShipmentService
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    decode_jwt_access_token,
    oauth_scheme_seller,
    oauth_scheme_delivery_partner,
)
from app.services.shipment_event import ShipmentEventService


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_shipment_service(session: SessionDep):
    yield ShipmentService(
        session,
        DeliveryPartnerService(session),
        ShipmentEventService(session),
    )


def get_seller_service(session: SessionDep):
    yield SellerService(session)


def get_delivery_partner_service(session: SessionDep):
    yield DeliveryPartnerService(session)


ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]
SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]
DeliveryPartnerServiceDep = Annotated[
    DeliveryPartnerService, Depends(get_delivery_partner_service)
]


async def get_access_token_data(token: str):
    data = decode_jwt_access_token(token)
    if not data or await is_jti_blacklisted(data["jti"]):
        raise InvalidTokenException(detail='Invalid or expired token')
    return data


async def get_seller_access_token_data(token: str = Depends(oauth_scheme_seller)):
    return await get_access_token_data(token)


async def get_delivery_partner_access_token_data(
    token: str = Depends(oauth_scheme_delivery_partner),
):
    return await get_access_token_data(token)


async def get_current_seller(
    session: SessionDep, data: dict = Depends(get_seller_access_token_data)
):
    seller = await session.get(Seller, UUID(data["user"]["id"]))
    if not seller:
        raise EnitityNotFoundException()
    if not seller.email_verified:
        raise EmailNotVerifiedException()
    return seller


async def get_current_delivery_partner(
    session: SessionDep, data: dict = Depends(get_seller_access_token_data)
):
    delivery_partner = await session.get(DeliveryPartner, UUID(data["user"]["id"]))
    if not delivery_partner:
        raise EnitityNotFoundException()
    if not delivery_partner.email_verified:
        raise EmailNotVerifiedException()
    return delivery_partner


SellerDep = Annotated[Seller, Depends(get_current_seller)]
DeliveryPartnerDep = Annotated[DeliveryPartner, Depends(get_current_delivery_partner)]
