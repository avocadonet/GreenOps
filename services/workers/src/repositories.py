from uuid import UUID

from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional
from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    SqlAlchemyRepository,
    provide,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.average_load import AverageLoadModel
from shared.db.incident import IncidentModel
from shared.db.metric import MetricModel
from shared.db.peak_load import PeakLoadModel
from shared.db.threshold import ThresholdModel
from shared.dtos.incident import CreateIncidentDTO
from shared.dtos.metric import CreateMetricDTO
from shared.dtos.peak_load import CreatePeakLoadDTO

_retort = ConversionRetort()

_metric_create_mapper = _retort.get_converter(
    CreateMetricDTO,
    MetricModel,
    recipe=[allow_unlinked_optional(P[MetricModel].metric_id)],
)
_peak_load_create_mapper = _retort.get_converter(
    CreatePeakLoadDTO,
    PeakLoadModel,
    recipe=[allow_unlinked_optional(P[PeakLoadModel].peak_id)],
)
_incident_create_mapper = _retort.get_converter(
    CreateIncidentDTO,
    IncidentModel,
    recipe=[
        allow_unlinked_optional(P[IncidentModel].incident_id),
        allow_unlinked_optional(P[IncidentModel].status),
    ],
)


@provide(
    SqlalchemyConfig[CreateMetricDTO, MetricModel, MetricModel](
        create_mapper=_metric_create_mapper,
        entity_mapper=lambda x: x,
        model_mapper=lambda x: x,
        model=MetricModel,
    )
)
class MetricDatabaseRepository(
    ErrorHandlingSqlAlchemyRepository[CreateMetricDTO, MetricModel, MetricModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=MetricModel, id_attr="metric_id"
        )

    @decorators.create
    async def create(self, dto: CreateMetricDTO) -> MetricModel: ...


@provide(
    SqlalchemyConfig[CreatePeakLoadDTO, PeakLoadModel, PeakLoadModel](
        create_mapper=_peak_load_create_mapper,
        entity_mapper=lambda x: x,
        model_mapper=lambda x: x,
        model=PeakLoadModel,
    )
)
class PeakLoadDatabaseRepository(
    ErrorHandlingSqlAlchemyRepository[CreatePeakLoadDTO, PeakLoadModel, PeakLoadModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=PeakLoadModel, id_attr="peak_id"
        )

    @decorators.create
    async def create(self, dto: CreatePeakLoadDTO) -> PeakLoadModel: ...


@provide(
    SqlalchemyConfig[CreateIncidentDTO, IncidentModel, IncidentModel](
        create_mapper=_incident_create_mapper,
        entity_mapper=lambda x: x,
        model_mapper=lambda x: x,
        model=IncidentModel,
    )
)
class IncidentDatabaseRepository(
    ErrorHandlingSqlAlchemyRepository[CreateIncidentDTO, IncidentModel, IncidentModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=IncidentModel, id_attr="incident_id"
        )

    @decorators.create
    async def create(self, dto: CreateIncidentDTO) -> IncidentModel: ...


@provide(
    SqlalchemyConfig[None, ThresholdModel, ThresholdModel](
        create_mapper=lambda x: x,
        entity_mapper=lambda x: x,
        model_mapper=lambda x: x,
        model=ThresholdModel,
    )
)
class ThresholdReadDatabaseRepository(
    SqlAlchemyRepository[None, ThresholdModel, ThresholdModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=ThresholdModel, id_attr="threshold_id"
        )

    @decorators.read(raise_if_missing=False)
    async def read_by_sensor(self, sensor_id: UUID) -> ThresholdModel | None:
        return (
            select(ThresholdModel)
            .where(ThresholdModel.sensor_id == sensor_id)
            .limit(1)
        )


@provide(
    SqlalchemyConfig[None, AverageLoadModel, AverageLoadModel](
        create_mapper=lambda x: x,
        entity_mapper=lambda x: x,
        model_mapper=lambda x: x,
        model=AverageLoadModel,
    )
)
class AverageLoadReadDatabaseRepository(
    SqlAlchemyRepository[None, AverageLoadModel, AverageLoadModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=AverageLoadModel, id_attr="avg_load_id"
        )

    @decorators.read(raise_if_missing=False)
    async def read_latest(self, sensor_id: UUID) -> AverageLoadModel | None:
        return (
            select(AverageLoadModel)
            .where(AverageLoadModel.sensor_id == sensor_id)
            .order_by(AverageLoadModel.calculated_at.desc())
            .limit(1)
        )
