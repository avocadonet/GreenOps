from application.telemetry.service import EventPublisher, TelemetryService
from dishka import Provider, Scope, provide
from domain.spike_detector import SpikeDetector
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
        metrics,
        incidents,
        thresholds,
        avg_loads,
        peak_loads,
        detector: SpikeDetector,
        publisher: EventPublisher,
        tx,
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
