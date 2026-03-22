# src/domain/enums.py
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"           # Админ всей системы
    ORG_OWNER = "org_owner"   # Владелец конкретной организации
    VIEWER = "viewer"         # Только чтение метрик

class BuildingType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"

class ThresholdType(str, Enum):
    OVERLOAD = "overload"
    LEAKAGE = "leakage"

class IncidentType(str, Enum):
    SPIKE = "spike"
    ENERGY_THEFT = "energy_theft"

