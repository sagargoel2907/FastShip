from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from app.database.redis import add_jti_to_blacklist
from app.config import app_settings, MAIL_TEMPLATES_FOLDER

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

templates = Jinja2Templates(directory=MAIL_TEMPLATES_FOLDER)

router = APIRouter(prefix="/delivery-partner", tags=["Delivery partner"])


@router.post("/register", response_model=DeliveryPartnerRead)
async def register_delivery_partner(
    delivery_partner: DeliveryPartnerCreate, service: DeliveryPartnerServiceDep
):
    return await service.create(delivery_partner)


@router.get("/dashboard")
async def dashboard(delivery_partner: DeliveryPartnerDep):
    return delivery_partner


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


@router.patch("/update", response_model=DeliveryPartnerRead)
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


@router.get("/verify")
async def verify_email(token: str, service: DeliveryPartnerServiceDep):
    await service.verify_user_email_with_token(token)
    return {"details": "Email Verified!"}

@router.get("/forgot-password")
async def forgot_password(email: EmailStr, service: DeliveryPartnerServiceDep):
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
    service: DeliveryPartnerServiceDep,
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



@router.get("/{id}", response_model=DeliveryPartnerRead)
async def get_delivery_partner(id: UUID, service: DeliveryPartnerServiceDep):
    return await service.get(id)

