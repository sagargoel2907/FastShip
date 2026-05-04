from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from app.config import MAIL_TEMPLATES_FOLDER, app_settings
from app.database.redis import add_jti_to_blacklist

from ..dependencies import SellerDep, SellerServiceDep, get_seller_access_token_data
from ..schemas.seller import SellerCreate, SellerRead

templates = Jinja2Templates(directory=MAIL_TEMPLATES_FOLDER)

router = APIRouter(prefix="/seller", tags=["Seller"])


@router.post("/register", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.create(seller)


@router.get("/dashboard")
async def dashboard(seller: SellerDep):
    return seller


@router.post("/token")
async def token(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.get_access_token(request_form.username, request_form.password)

    return {"access_token": token, "type": "jwt"}


@router.post("/logout")
async def logout(token_data: Annotated[dict, Depends(get_seller_access_token_data)]):
    await add_jti_to_blacklist(token_data["jti"])
    return {"details": "Successfully logged out!"}


@router.get("/", response_model=list[SellerRead])
async def get_all_sellers(service: SellerServiceDep):
    return await service.get_all_sellers()


@router.get("/verify")
async def verify_email(token: str, service: SellerServiceDep):
    await service.verify_user_email_with_token(token)
    return {"details": "Email Verified!"}


@router.get("/forgot-password")
async def forgot_password(email: EmailStr, service: SellerServiceDep):
    await service.send_password_reset_email(email, router.prefix)
    return {
        "details": "Please check email for the password reset link",
    }


@router.get("/reset-password-form")
def reset_password_form(token: str, request: Request):
    return templates.TemplateResponse(
        request=request,
        context={
            "reset_password_action_url": f"http://{app_settings.APP_DOMAIN}{router.prefix}/reset-password",
            "reset_token": token,
        },
        name="reset_password_form.html",
    )


@router.post("/reset-password")
async def reset_password(
    token: Annotated[str, Form()],
    password: Annotated[str, Form()],
    service: SellerServiceDep,
    request: Request,
):
    if await service.reset_password(token, password):
        return templates.TemplateResponse(
            request=request,
            name="reset_password_success.html",
        )
    else:
        return templates.TemplateResponse(
            request=request,
            name="reset_password_fail.html",
        )


@router.get("/{id}", response_model=SellerRead)
async def get_seller(id: UUID, service: SellerServiceDep):
    return await service.get(id)
