from pydantic import BaseModel, EmailStr


class BaseSeller(BaseModel):
    name: str
    email: EmailStr


class SellerRead(BaseSeller):
    pass


class SellerCreate(BaseSeller):
    password: str


class Shipment(BaseModel):
    content: str


class SellerShipments(BaseModel):
    shipments: list[Shipment]
    total_shipments: int
    page: int
