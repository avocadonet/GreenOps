from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.average_load.repository import AverageLoadRepository
from infrastructure.db.building.repository import BuildingReadRepository
from infrastructure.db.energy_balance.repository import EnergyBalanceRepository
from infrastructure.db.metric.repository import MetricReadRepository
from infrastructure.db.sensor.repository import SensorReadRepository


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    buildings = provide(BuildingReadRepository)
    sensors = provide(SensorReadRepository)
    metrics = provide(MetricReadRepository)
    energy_balances = provide(EnergyBalanceRepository)
    avg_loads = provide(AverageLoadRepository)
