from uuid import UUID

from adaptix.conversion import ConversionRetort
from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import AsyncSqlAlchemyGateway, SqlAlchemyRepository, provide
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.threshold import ThresholdModel
from shared.entities.threshold import Threshold

_retort = ConversionRetort()

@provide(
    SqlalchemyConfig[None, Threshold, ThresholdModel](
        create_mapper=lambda x: x,
        entity_mapper=lambda x: x,
        model_mapper=_retort.get_converter(ThresholdModel, Threshold),
        model=ThresholdModel,
    )
)
class ThresholdReadDatabaseRepository(
    SqlAlchemyRepository[None, Threshold, ThresholdModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=ThresholdModel, id_attr="threshold_id"
        )

    @decorators.read(raise_if_missing=False)
    async def read_by_sensor(self, sensor_id: UUID) -> Threshold | None:
        return (
            select(ThresholdModel)
            .where(ThresholdModel.sensor_id == sensor_id)
            .limit(1)
        )
