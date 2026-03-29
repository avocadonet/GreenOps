from application.building.service import BuildingService
from application.sensor.service import SensorService
from application.threshold.service import ThresholdService
from application.unit.service import UnitService
from dishka import Provider, Scope, provide


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    buildings = provide(BuildingService)
    units = provide(UnitService)
    sensors = provide(SensorService)
    thresholds = provide(ThresholdService)
