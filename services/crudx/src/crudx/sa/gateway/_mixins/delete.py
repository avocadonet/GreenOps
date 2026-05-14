from sqlalchemy.exc import NoResultFound

from .base import Base
from .utils import get_select_by_id_params


class DeleteMixin[Model](Base[Model]):
    async def delete(self, model: Model) -> Model | None:
        if saved := await self._get(**get_select_by_id_params(model, self._id_attr)):
            await self._session.delete(saved)
            await self._session.flush()
            return saved
        raise NoResultFound
