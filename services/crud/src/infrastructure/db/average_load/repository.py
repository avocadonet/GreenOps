from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy.ext.asyncio import AsyncSession

from domain.average_load.repository import AverageLoadRepository
from shared.db.average_load import AverageLoadModel
from shared.dtos.average_load import CreateAverageLoadDTO
from shared.entities.average_load import AverageLoad

from . import mappers


@provide(
    SqlalchemyConfig[CreateAverageLoadDTO, AverageLoad, AverageLoadModel](
        create_mapper=mappers.average_load__create_mapper,
        entity_mapper=mappers.average_load__map_to_db,
        model_mapper=mappers.average_load__map_from_db,
        model=AverageLoadModel,
    )
)
class AverageLoadDatabaseRepository(
    AverageLoadRepository,
    ErrorHandlingSqlAlchemyRepository[
        CreateAverageLoadDTO, AverageLoad, AverageLoadModel
    ],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=AverageLoadModel, id_attr="avg_load_id"
        )

    @decorators.create
    async def create(self, dto: CreateAverageLoadDTO) -> AverageLoad: ...
