from application.average_load.service import AverageLoadService
from application.energy_balance.service import EnergyBalanceService
from dishka import Provider, Scope, provide
from domain.average_load_calculator import AverageLoadCalculator
from domain.energy_balance_calculator import EnergyBalanceCalculator
from infrastructure.db.average_load.repository import AverageLoadRepository
from infrastructure.db.building.repository import BuildingReadRepository
from infrastructure.db.energy_balance.repository import EnergyBalanceRepository
from infrastructure.db.metric.repository import MetricReadRepository
from infrastructure.db.sensor.repository import SensorReadRepository


class ServiceProvider(Provider):
    scope = Scope.APP

    avg_load_calculator = provide(AverageLoadCalculator)
    energy_balance_calculator = provide(EnergyBalanceCalculator)

    @provide(scope=Scope.REQUEST)
    def get_average_load_service(
        self,
        sensors: SensorReadRepository,
        metrics: MetricReadRepository,
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
        buildings: BuildingReadRepository,
        sensors: SensorReadRepository,
        metrics: MetricReadRepository,
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
