import asyncio
from typing import AsyncIterable

from crudx.sa.transaction import AsyncTransactionsDatabaseGateway
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from faststream.nats import NatsBroker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from config import Config, get_config
from database import get_engine, get_session_maker
from nats_publisher import NatsEventPublisher
from repositories import (
    AverageLoadReadDatabaseRepository,
    IncidentDatabaseRepository,
    MetricDatabaseRepository,
    PeakLoadDatabaseRepository,
    ThresholdReadDatabaseRepository,
)
from spike_detector import SpikeDetector
from telemetry import TelemetryService


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def config(self) -> Config:
        return get_config()

    @provide(scope=Scope.APP)
    def engine(self, config: Config) -> AsyncEngine:
        return get_engine(config.database_url)

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
        return get_session_maker(engine)

    @provide(scope=Scope.REQUEST)
    async def session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session
            await session.commit()
        await asyncio.shield(session.close())

    @provide(scope=Scope.REQUEST)
    def transaction(self, session: AsyncSession) -> AsyncTransactionsDatabaseGateway:
        return AsyncTransactionsDatabaseGateway(session)

    spike_detector = provide(SpikeDetector, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def publisher(self, broker: NatsBroker) -> NatsEventPublisher:
        return NatsEventPublisher(broker)

    metrics = provide(MetricDatabaseRepository, scope=Scope.REQUEST)
    incidents = provide(IncidentDatabaseRepository, scope=Scope.REQUEST)
    peak_loads = provide(PeakLoadDatabaseRepository, scope=Scope.REQUEST)
    thresholds = provide(ThresholdReadDatabaseRepository, scope=Scope.REQUEST)
    avg_loads = provide(AverageLoadReadDatabaseRepository, scope=Scope.REQUEST)

    telemetry = provide(TelemetryService, scope=Scope.REQUEST)


def create_container(broker: NatsBroker) -> AsyncContainer:
    return make_async_container(
        AppProvider(),
        context={NatsBroker: broker},
    )
