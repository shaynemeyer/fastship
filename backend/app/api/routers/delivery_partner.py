from math import ceil
from typing import Annotated, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from sqlmodel import asc, desc, select

from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.shipment import ShipmentRead
from app.config import app_settings

from app.api.dependencies import (
    DeliveryPartnerDep,
    DeliveryPartnerServiceDep,
    SessionDep,
    get_delivery_partner_access_token,
)
from app.api.schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerRead,
    DeliveryPartnerShipments,
    DeliveryPartnerUpdate,
)
from app.api.tag import APITag
from app.core.exceptions import EntityNotFound
from app.database.models import Shipment
from app.database.redis import add_jti_to_blacklist
from app.utils import TEMPLATE_DIR

router = APIRouter(prefix="/partner", tags=[APITag.PARTNER])


### Register a new delivery partner
@router.post("/signup", response_model=DeliveryPartnerRead)
async def register_delivery_partner(
    partner: DeliveryPartnerCreate, service: DeliveryPartnerServiceDep
):
    return await service.add(partner)


### Login a delivery partner
@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: DeliveryPartnerServiceDep,
):
    token = await service.token(request_form.username, request_form.password)
    return {"access_token": token, "type": "jwt"}


### Update the delivery partner
@router.post("/", response_model=DeliveryPartnerRead)
async def update_delivery_partner(
    partner_update: DeliveryPartnerUpdate,
    partner: DeliveryPartnerDep,
    service: DeliveryPartnerServiceDep,
):
    update = partner_update.model_dump(exclude_none=True)

    if not update:
        raise EntityNotFound

    return await service.update(partner.sqlmodel_update(update))


### Logout a delivery partner
@router.get("/logout")
async def logout_delivery_partner(
    token_data: Annotated[dict, Depends(get_delivery_partner_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])
    return {"detail": "Successfully logged out!"}


### Verify Seller Email
@router.get("/verify")
async def verify_delivery_partner_email(token: str, service: DeliveryPartnerServiceDep):
    await service.verify_email(token)
    return {"detail": "Account verified"}


### Email Password Reset Link
@router.get("/forgot_password")
async def forgot_password(email: EmailStr, service: DeliveryPartnerServiceDep):
    await service.send_password_reset_link(email, router.prefix)
    return {"detail": "Check email for password reset link"}


### Reset Delivery Partner Password
@router.post("/reset_password")
async def reset_password(
    request: Request,
    token: str,
    password: Annotated[str, Form()],
    service: DeliveryPartnerServiceDep,
):
    is_success = await service.reset_password(token=token, password=password)

    templates = Jinja2Templates(TEMPLATE_DIR)

    return templates.TemplateResponse(
        request=request,
        name=(
            "password/reset_success.html"
            if is_success
            else "password/reset_failed.html"
        ),
    )


### Password Reset Form
@router.get("/reset_password_form")
async def get_reset_password_form(request: Request, token: str):
    templates = Jinja2Templates(TEMPLATE_DIR)

    return templates.TemplateResponse(
        request=request,
        name="password/reset.html",
        context={
            "reset_url": f"http://{app_settings.APP_DOMAIN}{router.prefix}/reset_password?token={token}",
        },
    )


### Get seller profile
@router.get("/me", response_model=DeliveryPartnerRead)
async def get_partner_profile(partner: DeliveryPartnerDep):
    return partner


### Get all shipments assigned to the delivery partner
@router.get("/shipments", response_model=list[DeliveryPartnerShipments])
async def get_shipments(
    partner: DeliveryPartnerDep,
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
):
    result = await session.scalars(
        select(Shipment)
        .where(Shipment.delivery_partner_id == partner.id)
        .limit(pagination.pageSize)
        .offset((pagination.page - 1) * pagination.pageSize)
        .order_by(
            asc(Shipment.created_at)
            if pagination.order == "asc"
            else desc(Shipment.created_at)
        )
    )

    return {
        "shipments": result.all(),
        "total_shipments": len(partner.shipments),
        "page": pagination.page,
        "total_pages": ceil(len(partner.shipments) / pagination.pageSize),
    }
