from typing import Literal
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int = 1
    pageSize: int = 10
    order: Literal["asc", "desc"] = "asc"


def get_pagination_params(
    page: int = 1, pageSize: int = 10, order: Literal["asc", "desc"] = "asc"
):
    return PaginationParams(page=page, pageSize=pageSize, order=order)
