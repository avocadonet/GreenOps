from abc import ABC, abstractmethod

from shared.dtos.energy_balance import CreateEnergyBalanceDTO
from shared.entities.energy_balance import EnergyBalance


class EnergyBalanceRepository(ABC):
    @abstractmethod
    async def create(self, dto: CreateEnergyBalanceDTO) -> EnergyBalance: ...
