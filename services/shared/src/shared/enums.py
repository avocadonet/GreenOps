from enum import StrEnum


class BuildingType(StrEnum):
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"


class SensorType(StrEnum):
    COMMON = "common"        # attached to a Building (common/house meter)
    INDIVIDUAL = "individual"  # attached to a Unit (apartment meter)


class ThresholdType(StrEnum):
    UPPER = "upper"
    LOWER = "lower"


class TariffZone(StrEnum):
    DAY = "day"
    NIGHT = "night"


class WindowSize(StrEnum):
    HOUR = "hour"
    DAY = "day"


class IncidentType(StrEnum):
    OVERLOAD = "overload"
    LEAK = "leak"
    IDLE = "idle"


class IncidentSeverity(StrEnum):
    LOW = "low"
    HIGH = "high"


class IncidentStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
