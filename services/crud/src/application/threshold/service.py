from uuid import UUID

from application.transaction import TransactionsGateway
from domain.threshold.repository import ThresholdRepository
from shared.dtos.threshold import CreateThresholdDTO
from shared.entities.threshold import Threshold


class ThresholdService:
    def __init__(self, repository: ThresholdRepository, tx: TransactionsGateway) -> None:
        self._repository = repository
        self._tx = tx

    async def create(self, dto: CreateThresholdDTO) -> Threshold:
        return await self._repository.create(dto)

    async def read(self, threshold_id: UUID) -> Threshold:
        return await self._repository.read(threshold_id)

    async def delete(self, threshold_id: UUID) -> Threshold:
        async with self._tx:
            threshold = await self._repository.read(threshold_id)
            return await self._repository.delete(threshold)
