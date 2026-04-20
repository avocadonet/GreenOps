from datetime import datetime
from uuid import UUID

from application.auth.enums import PermissionsEnum
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from domain.energy_balance.repository import EnergyBalanceRepository
from infrastructure.api.dependencies import require_permission

from .schemas import EnergyBalanceResponse

router = APIRouter(
    prefix="/energy-balances",
    route_class=DishkaRoute,
    tags=["energy-balances"],
    dependencies=[Depends(require_permission(PermissionsEnum.CAN_READ_ENERGY_BALANCE))],
)


@router.get("", response_model=list[EnergyBalanceResponse])
async def list_energy_balances(
    building_id: UUID,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    repository: FromDishka[EnergyBalanceRepository] = ...,
):
    balances = await repository.list_by_building(building_id, date_from, date_to)
    return [
        EnergyBalanceResponse(
            balance_id=b.balance_id,
            building_id=b.building_id,
            period_start=b.period_start,
            period_end=b.period_end,
            loss_kwh=b.loss_kwh,
            loss_percent=b.loss_percent,
        )
        for b in balances
    ]
