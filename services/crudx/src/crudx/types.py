from dataclasses import dataclass
from typing import Generic, TypeVar

CreateDTO = TypeVar("CreateDTO")
Entity = TypeVar("Entity")
Model = TypeVar("Model")


@dataclass(slots=True)
class PageSpec:
    page: int = 1
    page_size: int = 50


@dataclass(slots=True)
class Page(Generic[Entity]):
    items: list[Entity]
    total: int
    page: int
    page_size: int
