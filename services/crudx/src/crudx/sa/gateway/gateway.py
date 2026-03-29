from ._mixins import CreateMixin, DeleteMixin, ReadMixin, UpdateMixin


class AsyncSqlAlchemyGateway[Model](
    CreateMixin[Model], ReadMixin[Model], UpdateMixin[Model], DeleteMixin[Model]
):
    pass
