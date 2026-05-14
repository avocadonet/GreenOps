import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from application.auth.enums import PermissionsEnum
from application.auth.permissions.builder import PermissionBuilder
from application.auth.permissions.org_provider import OrgPermissionProvider
from application.auth.permissions.user_provider import UserPermissionProvider
from domain.building.repository import BuildingRepository
from domain.energy_balance.repository import EnergyBalanceRepository
from domain.energy_balance_calculator import EnergyBalanceCalculator
from domain.metric.repository import MetricRepository
from domain.sensor.repository import SensorRepository
from domain.users.entities import User
from domain.users.role_getter import RoleGetter
from shared.dtos.energy_balance import CreateEnergyBalanceDTO
from shared.entities.energy_balance import EnergyBalance
from shared.enums import SensorType

logger = logging.getLogger(__name__)


class EnergyBalanceService:
    def __init__(
        self,
        buildings: BuildingRepository,
        sensors: SensorRepository,
        metrics: MetricRepository,
        balances: EnergyBalanceRepository,
        calculator: EnergyBalanceCalculator,
        role_getter: RoleGetter,
    ) -> None:
        self._buildings = buildings
        self._sensors = sensors
        self._metrics = metrics
        self._balances = balances
        self._calculator = calculator
        self._role_getter = role_getter

    def _check(self, user: User, *perms: PermissionsEnum) -> None:
        PermissionBuilder().providers(UserPermissionProvider(user)).add(*perms).apply()

    async def _check_org(
        self, user: User, organization_id: int, *perms: PermissionsEnum
    ) -> None:
        org_role = await self._role_getter(user, organization_id)
        PermissionBuilder().providers(OrgPermissionProvider(org_role)).add(
            *perms
        ).apply()

    async def list_by_building(
        self,
        user: User,
        building_id: UUID,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[EnergyBalance]:
        building = await self._buildings.read(building_id)
        if building.organization_id is not None:
            await self._check_org(
                user, building.organization_id, PermissionsEnum.CAN_READ_ENERGY_BALANCE
            )
        else:
            self._check(user, PermissionsEnum.CAN_READ_ENERGY_BALANCE)
        return await self._balances.list_by_building(building_id, date_from, date_to)

    async def run_daily(self) -> None:
        now = datetime.now(tz=timezone.utc)
        yesterday_start = (now - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        yesterday_end = yesterday_start + timedelta(days=1)

        buildings = await self._buildings.list_all()
        for building in buildings:
            try:
                await self._compute_for_building(
                    building, yesterday_start, yesterday_end
                )
            except Exception:
                logger.exception(
                    "Failed to compute EnergyBalance for building %s",
                    building.building_id,
                )

    async def _compute_for_building(
        self, building, period_start: datetime, period_end: datetime
    ) -> None:
        sensors = await self._sensors.list_by_building(building.building_id)

        common_sensor = next(
            (s for s in sensors if s.sensor_type == SensorType.COMMON), None
        )
        if common_sensor is None:
            logger.debug(
                "Building %s has no COMMON sensor — skipping", building.building_id
            )
            return

        common_metrics = await self._metrics.list_by_sensor_in_range(
            common_sensor.sensor_id, period_start, period_end
        )
        common_kwh = sum(m.value for m in common_metrics)

        individual_sensors = [
            s for s in sensors if s.sensor_type == SensorType.INDIVIDUAL
        ]
        individual_sum = 0.0
        for sensor in individual_sensors:
            metrics = await self._metrics.list_by_sensor_in_range(
                sensor.sensor_id, period_start, period_end
            )
            individual_sum += sum(m.value for m in metrics)

        result = self._calculator.compute(
            common_kwh=common_kwh,
            individual_sum_kwh=individual_sum,
        )
        await self._balances.create(
            CreateEnergyBalanceDTO(
                building_id=building.building_id,
                period_start=period_start,
                period_end=period_end,
                loss_kwh=result.loss_kwh,
                loss_percent=result.loss_percent,
            )
        )
        logger.info(
            "EnergyBalance for building %s: loss=%.2f kWh (%.1f%%)",
            building.building_id,
            result.loss_kwh,
            result.loss_percent,
        )
