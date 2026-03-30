from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy.ext.asyncio import AsyncSession

from domain.energy_balance.repository import EnergyBalanceRepository
from shared.db.energy_balance import EnergyBalanceModel
from shared.dtos.energy_balance import CreateEnergyBalanceDTO
from shared.entities.energy_balance import EnergyBalance

from . import mappers


@provide(
    SqlalchemyConfig[CreateEnergyBalanceDTO, EnergyBalance, EnergyBalanceModel](
        create_mapper=mappers.energy_balance__create_mapper,
        entity_mapper=mappers.energy_balance__map_to_db,
        model_mapper=mappers.energy_balance__map_from_db,
        model=EnergyBalanceModel,
    )
)
class EnergyBalanceDatabaseRepository(
    EnergyBalanceRepository,
    ErrorHandlingSqlAlchemyRepository[
        CreateEnergyBalanceDTO, EnergyBalance, EnergyBalanceModel
    ],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=EnergyBalanceModel, id_attr="balance_id"
        )

    @decorators.create
    async def create(self, dto: CreateEnergyBalanceDTO) -> EnergyBalance: ...
