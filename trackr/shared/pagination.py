from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20

    model_config = ConfigDict(populate_by_name=True)


class PagedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    model_config = ConfigDict(populate_by_name=True)
