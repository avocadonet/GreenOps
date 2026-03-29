from application.average_load.service import AverageLoadService
from application.energy_balance.service import EnergyBalanceService
from dishka import Provider, Scope, provide
from domain.average_load_calculator import AverageLoadCalculator
from domain.energy_balance_calculator import EnergyBalanceCalculator


class ServiceProvider(Provider):
    scope = Scope.APP

    avg_load_calculator = provide(AverageLoadCalculator)
    energy_balance_calculator = provide(EnergyBalanceCalculator)

    @provide(scope=Scope.REQUEST)
    def get_average_load_service(
        self,
        sensors,
        metrics,
        avg_loads,
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
        buildings,
        sensors,
        metrics,
        balances,
        calculator: EnergyBalanceCalculator,
    ) -> EnergyBalanceService:
        return EnergyBalanceService(
            buildings=buildings,
            sensors=sensors,
            metrics=metrics,
            balances=balances,
            calculator=calculator,
        )
