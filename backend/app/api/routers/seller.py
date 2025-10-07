from math import ceil
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from sqlmodel import asc, desc, select

from app.api.dependencies import (
    SellerDep,
    SellerServiceDep,
    SessionDep,
    get_seller_access_token,
)
from app.api.schemas.pagination import PaginationParams, get_pagination_params
from app.api.schemas.seller import SellerCreate, SellerRead, SellerShipments
from app.api.tag import APITag
from app.config import app_settings
from app.core.exceptions import EntityNotFound
from app.database.models import Shipment
from app.database.redis import add_jti_to_blacklist
from app.utils import TEMPLATE_DIR

router = APIRouter(prefix="/seller", tags=[APITag.SELLER])


### Register a new seller
@router.post("/signup", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)


### Login a seller
@router.post("/token")
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.token(request_form.username, request_form.password)
    return {"access_token": token, "type": "jwt"}


### Logout a seller
@router.get("/logout")
async def logout_seller(token_data: Annotated[dict, Depends(get_seller_access_token)]):
    await add_jti_to_blacklist(token_data["jti"])
    return {"detail": "Successfully logged out!"}


### Verify Seller Email
@router.get("/verify")
async def verify_seller_email(token: str, service: SellerServiceDep):
    await service.verify_email(token)
    return {"detail": "Account verified"}


### Email Password Reset Link
@router.get("/forgot_password")
async def forgot_password(email: EmailStr, service: SellerServiceDep):
    await service.send_password_reset_link(email, router.prefix)
    return {"detail": "Check email for password reset link"}


### Reset Seller Password
@router.post("/reset_password")
async def reset_password(
    request: Request,
    token: str,
    password: Annotated[str, Form()],
    service: SellerServiceDep,
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
@router.get("/me", response_model=SellerRead)
async def get_seller_profile(seller: SellerDep):
    return seller


### Get all shipments assigned to the delivery partner
@router.get("/shipments", response_model=list[SellerShipments])
async def get_shipments(
    seller: SellerDep,
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
):
    result = await session.scalars(
        select(Shipment)
        .where(Shipment.seller_id == seller.id)
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
        "total_shipments": len(seller.shipments),
        "page": pagination.page,
        "total_pages": ceil(len(seller.shipments) / pagination.pageSize),
    }
