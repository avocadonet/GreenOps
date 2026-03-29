from .base import Base


class CreateMixin[Model](Base[Model]):
    async def insert_one(self, model: Model) -> Model:
        self._session.add(model)
        await self._session.flush()
        return model
