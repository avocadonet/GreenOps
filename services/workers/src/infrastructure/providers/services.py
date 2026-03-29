from application.telemetry.service import EventPublisher, TelemetryService
from application.transaction import TransactionsGateway
from dishka import Provider, Scope, provide
from domain.average_load.repository import AverageLoadReadRepository
from domain.incident.repository import IncidentRepository
from domain.metric.repository import MetricRepository
from domain.peak_load.repository import PeakLoadRepository
from domain.spike_detector import SpikeDetector
from domain.threshold.repository import ThresholdReadRepository
from faststream.kafka import KafkaBroker
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
        metrics: MetricRepository,
        incidents: IncidentRepository,
        thresholds: ThresholdReadRepository,
        avg_loads: AverageLoadReadRepository,
        peak_loads: PeakLoadRepository,
        detector: SpikeDetector,
        publisher: EventPublisher,
        tx: TransactionsGateway,
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
