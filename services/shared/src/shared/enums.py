from enum import StrEnum


class BuildingType(StrEnum):
    RESIDENTIAL = "RESIDENTIAL"
    INDUSTRIAL = "INDUSTRIAL"


class SensorType(StrEnum):
    COMMON = "COMMON"  # attached to a Building (common/house meter)
    INDIVIDUAL = "INDIVIDUAL"  # attached to a Unit (apartment meter)


class ThresholdType(StrEnum):
    UPPER = "UPPER"
    LOWER = "LOWER"


class TariffZone(StrEnum):
    DAY = "DAY"
    NIGHT = "NIGHT"


class WindowSize(StrEnum):
    HOUR = "HOUR"
    DAY = "DAY"


class IncidentType(StrEnum):
    OVERLOAD = "OVERLOAD"
    LEAK = "LEAK"
    IDLE = "IDLE"


class IncidentSeverity(StrEnum):
    LOW = "LOW"
    HIGH = "HIGH"


class IncidentStatus(StrEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
