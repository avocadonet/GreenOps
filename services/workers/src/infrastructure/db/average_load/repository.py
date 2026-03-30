from uuid import UUID

from adaptix.conversion import ConversionRetort
from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import AsyncSqlAlchemyGateway, SqlAlchemyRepository, provide
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.average_load import AverageLoadModel
from shared.entities.average_load import AverageLoad

_retort = ConversionRetort()

@provide(
    SqlalchemyConfig[None, AverageLoad, AverageLoadModel](
        create_mapper=lambda x: x,
        entity_mapper=lambda x: x,
        model_mapper=_retort.get_converter(AverageLoadModel, AverageLoad),
        model=AverageLoadModel,
    )
)
class AverageLoadReadDatabaseRepository(
    SqlAlchemyRepository[None, AverageLoad, AverageLoadModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=AverageLoadModel, id_attr="avg_load_id"
        )

    @decorators.read(raise_if_missing=False)
    async def read_latest(self, sensor_id: UUID) -> AverageLoad | None:
        return (
            select(AverageLoadModel)
            .where(AverageLoadModel.sensor_id == sensor_id)
            .order_by(AverageLoadModel.calculated_at.desc())
            .limit(1)
        )
