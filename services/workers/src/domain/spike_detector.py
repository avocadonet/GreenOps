from dataclasses import dataclass

from shared.entities.average_load import AverageLoad
from shared.entities.threshold import Threshold
from shared.enums import IncidentType, ThresholdType


@dataclass
class SpikeResult:
    incident_type: IncidentType


class SpikeDetector:
    """Pure, stateless spike detection logic. No I/O, no async."""

    IDLE_ZERO_THRESHOLD = 0.001  # values below this are treated as zero consumption
    IDLE_DURATION_SECONDS = 600  # 10 minutes of zero = idle

    def detect(
        self,
        value: float,
        duration_seconds: float,
        threshold: Threshold,
        baseline: AverageLoad | None,
    ) -> SpikeResult | None:
        if threshold.threshold_type == ThresholdType.UPPER and value > threshold.limit_value:
            return SpikeResult(incident_type=IncidentType.OVERLOAD)
        if threshold.threshold_type == ThresholdType.LOWER and value < threshold.limit_value:
            return SpikeResult(incident_type=IncidentType.LEAK)
        if value < self.IDLE_ZERO_THRESHOLD and duration_seconds > self.IDLE_DURATION_SECONDS:
            return SpikeResult(incident_type=IncidentType.IDLE)
        return None
