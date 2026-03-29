from abc import ABC, abstractmethod

from shared.dtos.incident import CreateIncidentDTO
from shared.entities.incident import Incident


class IncidentRepository(ABC):
    @abstractmethod
    async def create(self, dto: CreateIncidentDTO) -> Incident: ...
