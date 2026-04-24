from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from ..dependencies import SellerDep, SellerServiceDep
from ..schemas.seller import SellerCreate, SellerRead

router = APIRouter(prefix="/seller", tags=["Seller"])


@router.post("/register", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.create(seller)


@router.get("/dashboard")
async def dashboard(seller: SellerDep):
    return seller


@router.get("/{id}", response_model=SellerRead)
async def get_seller(id: int, service: SellerServiceDep):
    return await service.get(id)


@router.post("/token")
async def token(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.get_access_token(request_form.username, request_form.password)

    return {"access_token": token, "type": "jwt"}
