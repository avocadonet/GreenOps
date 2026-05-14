from sqlalchemy.exc import NoResultFound

from .base import Base
from .utils import get_select_by_id_params


class UpdateMixin[Model](Base[Model]):
    async def update(self, model: Model) -> Model | None:
        if await self._get(**get_select_by_id_params(model, self._id_attr)):
            await self._session.merge(model)
            await self._session.flush()
            return model
        raise NoResultFound()
