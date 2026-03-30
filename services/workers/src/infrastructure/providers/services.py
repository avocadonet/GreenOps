from application.telemetry.service import EventPublisher, TelemetryService
from crudx.sa.transaction import AsyncTransactionsDatabaseGateway
from dishka import Provider, Scope, provide
from domain.spike_detector import SpikeDetector
from faststream.kafka import KafkaBroker
from infrastructure.db.average_load.repository import AverageLoadReadDatabaseRepository
from infrastructure.db.incident.repository import IncidentDatabaseRepository
from infrastructure.db.metric.repository import MetricDatabaseRepository
from infrastructure.db.peak_load.repository import PeakLoadDatabaseRepository
from infrastructure.db.threshold.repository import ThresholdReadDatabaseRepository
from infrastructure.kafka.publisher import KafkaEventPublisher


class ServiceProvider(Provider):
    scope = Scope.APP

    spike_detector = provide(SpikeDetector)

    @provide(scope=Scope.APP)
    def get_publisher(self, broker: KafkaBroker) -> EventPublisher:
        return KafkaEventPublisher(broker)

    @provide(scope=Scope.REQUEST)
    def get_telemetry_service(
        self,
        metrics: MetricDatabaseRepository,
        incidents: IncidentDatabaseRepository,
        thresholds: ThresholdReadDatabaseRepository,
        avg_loads: AverageLoadReadDatabaseRepository,
        peak_loads: PeakLoadDatabaseRepository,
        detector: SpikeDetector,
        publisher: EventPublisher,
        tx: AsyncTransactionsDatabaseGateway,
    ) -> TelemetryService:
        return TelemetryService(
            metrics=metrics,
            incidents=incidents,
            thresholds=thresholds,
            avg_loads=avg_loads,
            peak_loads=peak_loads,
            detector=detector,
            publisher=publisher,
            tx=tx,
        )
