import logging
from typing import Protocol

from application.transaction import TransactionsGateway
from domain.average_load.repository import AverageLoadReadRepository
from domain.incident.repository import IncidentRepository
from domain.metric.repository import MetricRepository
from domain.peak_load.repository import PeakLoadRepository
from domain.spike_detector import SpikeDetector
from domain.threshold.repository import ThresholdReadRepository
from shared.dtos.incident import CreateIncidentDTO, IncidentCreatedEvent
from shared.dtos.metric import CreateMetricDTO
from shared.dtos.peak_load import CreatePeakLoadDTO
from shared.enums import IncidentSeverity

logger = logging.getLogger(__name__)


class EventPublisher(Protocol):
    async def publish_incident(self, event: IncidentCreatedEvent) -> None: ...


class TelemetryService:
    def __init__(
        self,
        metrics: MetricRepository,
        incidents: IncidentRepository,
        thresholds: ThresholdReadRepository,
        avg_loads: AverageLoadReadRepository,
        peak_loads: PeakLoadRepository,
        detector: SpikeDetector,
        publisher: EventPublisher,
        tx: TransactionsGateway,
    ) -> None:
        self._metrics = metrics
        self._incidents = incidents
        self._thresholds = thresholds
        self._avg_loads = avg_loads
        self._peak_loads = peak_loads
        self._detector = detector
        self._publisher = publisher
        self._tx = tx

    async def process(self, dto: CreateMetricDTO) -> None:
        async with self._tx:
            await self._metrics.create(dto)

            threshold = await self._thresholds.read_by_sensor(dto.sensor_id)
            if threshold is None:
                return  # no threshold configured — nothing to detect

            baseline = await self._avg_loads.read_latest(dto.sensor_id)
            result = self._detector.detect(
                value=dto.value,
                duration_seconds=0,  # MVP: stateless, no elapsed-time tracking
                threshold=threshold,
                baseline=baseline,
            )
            if result is None:
                return

            severity = (
                IncidentSeverity.HIGH
                if dto.value > threshold.limit_value * 1.5
                else IncidentSeverity.LOW
            )
            peak = await self._peak_loads.create(
                CreatePeakLoadDTO(
                    sensor_id=dto.sensor_id,
                    max_value=dto.value,
                    duration_seconds=0,
                    detected_at=dto.recorded_at,
                )
            )
            incident = await self._incidents.create(
                CreateIncidentDTO(
                    incident_type=result.incident_type,
                    severity=severity,
                    threshold_id=threshold.threshold_id,
                    peak_load_id=peak.peak_id,
                )
            )

        # Publish outside the DB transaction — message broker is not part of DB tx
        await self._publisher.publish_incident(
            IncidentCreatedEvent(
                incident_id=incident.incident_id,
                incident_type=incident.incident_type,
                severity=incident.severity,
                threshold_id=incident.threshold_id,
                peak_load_id=incident.peak_load_id,
            )
        )
        logger.info(
            "Incident created: %s severity=%s sensor=%s",
            incident.incident_type,
            incident.severity,
            dto.sensor_id,
        )
