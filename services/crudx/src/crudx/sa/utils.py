from typing import cast

from crudx.types import Page
from sqlalchemy import Select


def from_query[Entity](query: Select) -> Entity | list[Entity] | Page:
    return cast(Entity | list[Entity] | Page, query)


def from_dto[Dto, Entity](dto: Dto) -> Entity | list[Entity]:
    return cast(Entity | list[Entity], dto)
