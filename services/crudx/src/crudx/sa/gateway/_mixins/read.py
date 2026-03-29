from typing import Any, Sequence

from crudx.types import PageSpec
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound

from .base import Base


class ReadMixin[Model](Base[Model]):
    async def select_all(self, page: PageSpec) -> Sequence[Model]:
        stmt = (
            select(self._model)
            .offset((page.page - 1) * page.page_size)
            .limit(page.page_size)
        )
        return (await self._session.execute(stmt)).scalars().all()

    async def select_by_fields_all(self, **params: [str, Any]) -> Sequence[Model]:
        stmt = select(self._model).filter_by(**params)
        return (await self._session.execute(stmt)).scalars().all()

    async def select_by_fields_first(self, **params: [str, Any]) -> Model:
        stmt = select(self._model).filter_by(**params)
        return (await self._session.execute(stmt)).scalar_one()

    async def select_by_query_all(self, stmt: Select) -> Sequence[Model]:
        return (await self._session.execute(stmt)).scalars().all()

    async def select_by_query_first(self, stmt: Select) -> Model:
        return (await self._session.execute(stmt)).scalar_one()
