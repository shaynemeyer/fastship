from typing import Sequence
from uuid import UUID
from sqlmodel import select
from app.api.schemas.delivery_partner import DeliveryPartnerCreate
from app.core.exceptions import DeliveryPartnerNotAvailable, InvalidToken
from app.database.models import DeliveryPartner, Location, Shipment
from app.services.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import decode_url_safe_token


class DeliveryPartnerService(UserService):
    def __init__(self, session: AsyncSession):
        super().__init__(DeliveryPartner, session)  # type: ignore

    async def add(self, delivery_partner: DeliveryPartnerCreate):
        partner: DeliveryPartner = await self._add_user(
            delivery_partner.model_dump(exclude={"serviceable_zip_codes"}),
            "partner",
        )  # type: ignore
        for zip_code in delivery_partner.serviceable_zip_codes:
            location = await self.session.get(Location, zip_code)
            partner.serviceable_locations.append(
                location if location else Location(zip_code=zip_code)
            )
        return await self._update(partner)

    async def get_partner_by_zipcode(self, zipcode: int) -> Sequence[DeliveryPartner]:
        return (
            await self.session.scalars(
                select(DeliveryPartner)
                .join(DeliveryPartner.serviceable_locations)  # type: ignore
                .where(Location.zip_code == zipcode)
            )
        ).all()

    async def get_shipments_by_partner(self, token: str) -> Sequence[Shipment]:
        token_data = decode_url_safe_token(token)
        # Validate the token
        if not token_data:
            raise InvalidToken
        userId = UUID(token_data["id"])

        return (
            await self.session.scalars(
                select(DeliveryPartner.shipments).where(DeliveryPartner.id == userId)
            )
        ).all()

    async def assign_shipment(self, shipment: Shipment):
        eligible_partners = await self.get_partner_by_zipcode(shipment.destination)

        for partner in eligible_partners:
            if partner.current_handling_capacity > 0:
                partner.shipments.append(shipment)
                return partner

        raise DeliveryPartnerNotAvailable

    async def update(self, partner: DeliveryPartner):
        return await self._update(partner)

    async def token(self, email, password) -> str:
        return await self._generate_token(email=email, password=password)
