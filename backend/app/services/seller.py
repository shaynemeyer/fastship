from uuid import UUID
from typing import Sequence
from app.core.exceptions import InvalidToken
from app.services.user import UserService

from passlib.context import CryptContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.seller import SellerCreate
from app.database.models import Seller, Shipment
from app.utils import decode_url_safe_token

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SellerService(UserService):
    def __init__(self, session: AsyncSession):
        super().__init__(Seller, session)  # type: ignore

    async def add(self, seller_create: SellerCreate) -> Seller:
        return await self._add_user(seller_create.model_dump(), router_prefix="seller")  # type: ignore

    async def token(self, email, password) -> str:
        return await self._generate_token(email=email, password=password)

    async def get_shipments_by_seller(self, token: str) -> Sequence[Shipment]:
        token_data = decode_url_safe_token(token)
        # Validate the token
        if not token_data:
            raise InvalidToken
        userId = UUID(token_data["id"])
        return (
            await self.session.scalars(select(Shipment).where(Shipment.seller_id == userId))  # type: ignore
        ).all()
