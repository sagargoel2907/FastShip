from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.database.redis import add_jti_to_blacklist

from ..dependencies import SellerDep, SellerServiceDep, get_seller_access_token_data
from ..schemas.seller import SellerCreate, SellerRead

router = APIRouter(prefix="/seller", tags=["Seller"])


@router.post("/register", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.create(seller)


@router.get("/dashboard")
async def dashboard(seller: SellerDep):
    return seller


@router.get("/{id}", response_model=SellerRead)
async def get_seller(id: UUID, service: SellerServiceDep):
    return await service.get(id)


@router.post("/token")
async def token(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.get_access_token(request_form.username, request_form.password)

    return {"access_token": token, "type": "jwt"}

@router.post('/logout')
async def logout(token_data: Annotated[dict, Depends(get_seller_access_token_data)]):
    await add_jti_to_blacklist(token_data['jti'])
    return {
        'details': 'Successfully logged out!'
    }

@router.get('/', response_model=list[SellerRead])
async def get_all_sellers(service: SellerServiceDep):
    return await service.get_all_sellers()