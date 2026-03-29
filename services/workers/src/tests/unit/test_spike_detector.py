import unittest
from uuid import uuid4

from domain.spike_detector import SpikeDetector
from shared.entities.threshold import Threshold
from shared.enums import IncidentType, TariffZone, ThresholdType


def _upper_threshold(limit: float) -> Threshold:
    return Threshold(
        threshold_id=uuid4(),
        sensor_id=uuid4(),
        limit_value=limit,
        threshold_type=ThresholdType.UPPER,
        tariff_zone=TariffZone.DAY,
    )


def _lower_threshold(limit: float) -> Threshold:
    return Threshold(
        threshold_id=uuid4(),
        sensor_id=uuid4(),
        limit_value=limit,
        threshold_type=ThresholdType.LOWER,
        tariff_zone=TariffZone.DAY,
    )


class TestSpikeDetector(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.detector = SpikeDetector()

    def test_no_spike_within_limit(self):
        result = self.detector.detect(
            value=80.0, duration_seconds=0,
            threshold=_upper_threshold(100.0), baseline=None,
        )
        self.assertIsNone(result)

    def test_overload_detected_above_limit(self):
        result = self.detector.detect(
            value=150.0, duration_seconds=0,
            threshold=_upper_threshold(100.0), baseline=None,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.incident_type, IncidentType.OVERLOAD)

    def test_overload_not_detected_at_exact_limit(self):
        result = self.detector.detect(
            value=100.0, duration_seconds=0,
            threshold=_upper_threshold(100.0), baseline=None,
        )
        self.assertIsNone(result)

    def test_leak_detected_below_lower_limit(self):
        result = self.detector.detect(
            value=5.0, duration_seconds=0,
            threshold=_lower_threshold(10.0), baseline=None,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.incident_type, IncidentType.LEAK)

    def test_idle_detected_zero_value_long_duration(self):
        result = self.detector.detect(
            value=0.0, duration_seconds=700,
            threshold=_upper_threshold(100.0), baseline=None,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.incident_type, IncidentType.IDLE)

    def test_idle_not_detected_within_duration_window(self):
        result = self.detector.detect(
            value=0.0, duration_seconds=300,
            threshold=_upper_threshold(100.0), baseline=None,
        )
        self.assertIsNone(result)

    def test_overload_takes_priority_over_idle(self):
        # value is above limit AND zero-ish — OVERLOAD fires first
        result = self.detector.detect(
            value=150.0, duration_seconds=700,
            threshold=_upper_threshold(100.0), baseline=None,
        )
        self.assertEqual(result.incident_type, IncidentType.OVERLOAD)
