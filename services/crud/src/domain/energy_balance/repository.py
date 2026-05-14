from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from shared.dtos.energy_balance import CreateEnergyBalanceDTO
from shared.entities.energy_balance import EnergyBalance


class EnergyBalanceRepository(ABC):
    @abstractmethod
    async def create(self, dto: CreateEnergyBalanceDTO) -> EnergyBalance: ...

    @abstractmethod
    async def list_by_building(
        self,
        building_id: UUID,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[EnergyBalance]: ...
