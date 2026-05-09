from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorModel(BaseModel):
    detail: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
