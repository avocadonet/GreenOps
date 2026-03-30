from application.average_load.service import AverageLoadService
from application.building.service import BuildingService
from application.energy_balance.service import EnergyBalanceService
from application.sensor.service import SensorService
from application.threshold.service import ThresholdService
from application.unit.service import UnitService
from dishka import Provider, Scope, provide

from domain.average_load.repository import AverageLoadRepository
from domain.average_load_calculator import AverageLoadCalculator
from domain.building.repository import BuildingRepository
from domain.energy_balance.repository import EnergyBalanceRepository
from domain.energy_balance_calculator import EnergyBalanceCalculator
from domain.metric.repository import MetricRepository
from domain.sensor.repository import SensorRepository


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    buildings = provide(BuildingService)
    units = provide(UnitService)
    sensors = provide(SensorService)
    thresholds = provide(ThresholdService)

    avg_load_calculator = provide(AverageLoadCalculator, scope=Scope.APP)
    energy_balance_calculator = provide(EnergyBalanceCalculator, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    def get_average_load_service(
        self,
        sensors: SensorRepository,
        metrics: MetricRepository,
        avg_loads: AverageLoadRepository,
        calculator: AverageLoadCalculator,
    ) -> AverageLoadService:
        return AverageLoadService(
            sensors=sensors,
            metrics=metrics,
            avg_loads=avg_loads,
            calculator=calculator,
        )

    @provide(scope=Scope.REQUEST)
    def get_energy_balance_service(
        self,
        buildings: BuildingRepository,
        sensors: SensorRepository,
        metrics: MetricRepository,
        balances: EnergyBalanceRepository,
        calculator: EnergyBalanceCalculator,
    ) -> EnergyBalanceService:
        return EnergyBalanceService(
            buildings=buildings,
            sensors=sensors,
            metrics=metrics,
            balances=balances,
            calculator=calculator,
        )
