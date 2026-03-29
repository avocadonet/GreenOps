from abc import ABCMeta

from sqlalchemy.ext.asyncio import AsyncSession


class Base[Model](metaclass=ABCMeta):
    def __init__(
        self,
        session: AsyncSession,
        *,
        sa_model: type[Model],
        id_attr: str | tuple[str, ...],
    ):
        self._session = session
        self._model = sa_model
        self._id_attr = id_attr

    async def _get(self, **params):
        return await self._session.get(self._model, params)
