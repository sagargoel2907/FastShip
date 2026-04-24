
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.database.models import Seller
from app.database.session import get_session
from app.services.seller import SellerService
from app.services.shipment import ShipmentService
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_jwt_token, oauth_scheme


SessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_shipment_service(session: SessionDep):
    yield ShipmentService(session)

def get_seller_service(session: SessionDep):
    yield SellerService(session)


ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]
SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]

def get_access_token_data(token: str = Depends(oauth_scheme)):
    data = decode_jwt_token(token)
    if not data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired JWT Token')
    return data

async def get_current_seller(session: SessionDep, data: dict = Depends(get_access_token_data)):
    return await session.get(Seller, data['user']['id'])

SellerDep = Annotated[Seller, Depends(get_current_seller)]
