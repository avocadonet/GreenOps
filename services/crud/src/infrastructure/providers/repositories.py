from dishka import Provider, Scope, provide

from domain.building.repository import BuildingRepository
from domain.sensor.repository import SensorRepository
from domain.threshold.repository import ThresholdRepository
from domain.unit.repository import UnitRepository
from infrastructure.db.building.repository import BuildingDatabaseRepository
from infrastructure.db.sensor.repository import SensorDatabaseRepository
from infrastructure.db.threshold.repository import ThresholdDatabaseRepository
from infrastructure.db.unit.repository import UnitDatabaseRepository


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    buildings = provide(source=BuildingDatabaseRepository, provides=BuildingRepository)
    units = provide(source=UnitDatabaseRepository, provides=UnitRepository)
    sensors = provide(source=SensorDatabaseRepository, provides=SensorRepository)
    thresholds = provide(source=ThresholdDatabaseRepository, provides=ThresholdRepository)
