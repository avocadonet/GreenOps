# src/domain/enums.py
from enum import Enum

class IncidentType(str, Enum):
    SPIKE = "spike"
    ENERGY_THEFT = "energy_theft"

