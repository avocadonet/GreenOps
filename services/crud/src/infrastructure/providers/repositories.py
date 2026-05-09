from dishka import Provider, Scope, provide

from domain.average_load.repository import AverageLoadRepository
from domain.building.repository import BuildingRepository
from domain.energy_balance.repository import EnergyBalanceRepository
from domain.metric.repository import MetricRepository
from domain.organization.repository import OrganizationRepository
from domain.sensor.repository import SensorRepository
from domain.threshold.repository import ThresholdRepository
from domain.unit.repository import UnitRepository
from domain.users.repositories import UserOrganizationRolesRepository
from infrastructure.db.average_load.repository import AverageLoadDatabaseRepository
from infrastructure.db.building.repository import BuildingDatabaseRepository
from infrastructure.db.energy_balance.repository import EnergyBalanceDatabaseRepository
from infrastructure.db.metric.repository import MetricDatabaseRepository
from infrastructure.db.organization.repository import OrganizationDatabaseRepository
from infrastructure.db.sensor.repository import SensorDatabaseRepository
from infrastructure.db.threshold.repository import ThresholdDatabaseRepository
from infrastructure.db.unit.repository import UnitDatabaseRepository
from infrastructure.db.user_organization_role.repository import UserOrganizationRolesDatabaseRepository


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    buildings = provide(source=BuildingDatabaseRepository, provides=BuildingRepository)
    units = provide(source=UnitDatabaseRepository, provides=UnitRepository)
    sensors = provide(source=SensorDatabaseRepository, provides=SensorRepository)
    thresholds = provide(
        source=ThresholdDatabaseRepository, provides=ThresholdRepository
    )
    metrics = provide(source=MetricDatabaseRepository, provides=MetricRepository)
    avg_loads = provide(
        source=AverageLoadDatabaseRepository, provides=AverageLoadRepository
    )
    energy_balances = provide(
        source=EnergyBalanceDatabaseRepository, provides=EnergyBalanceRepository
    )
    organizations = provide(
        source=OrganizationDatabaseRepository, provides=OrganizationRepository
    )
    user_org_roles = provide(
        source=UserOrganizationRolesDatabaseRepository,
        provides=UserOrganizationRolesRepository,
    )
