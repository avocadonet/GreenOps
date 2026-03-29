from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy.ext.asyncio import AsyncSession

from domain.peak_load.repository import PeakLoadRepository
from shared.db.peak_load import PeakLoadModel
from shared.dtos.peak_load import CreatePeakLoadDTO
from shared.entities.peak_load import PeakLoad

from . import mappers


@provide(
    SqlalchemyConfig[CreatePeakLoadDTO, PeakLoad, PeakLoadModel](
        create_mapper=mappers.peak_load__create_mapper,
        entity_mapper=mappers.peak_load__map_to_db,
        model_mapper=mappers.peak_load__map_from_db,
        model=PeakLoadModel,
    )
)
class PeakLoadDatabaseRepository(
    PeakLoadRepository,
    ErrorHandlingSqlAlchemyRepository[CreatePeakLoadDTO, PeakLoad, PeakLoadModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=PeakLoadModel, id_attr="peak_id"
        )

    @decorators.create
    async def create(self, dto: CreatePeakLoadDTO) -> PeakLoad: ...
