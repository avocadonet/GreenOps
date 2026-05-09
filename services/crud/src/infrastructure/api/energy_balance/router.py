from datetime import datetime
from uuid import UUID

from application.energy_balance.service import EnergyBalanceService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from domain.users.entities import User
from fastapi import APIRouter, Depends

from infrastructure.api.dependencies import get_current_user

from .schemas import EnergyBalanceResponse

router = APIRouter(
    prefix="/energy-balances",
    route_class=DishkaRoute,
    tags=["energy-balances"],
)


@router.get("", response_model=list[EnergyBalanceResponse])
async def list_energy_balances(
    building_id: UUID,
    service: FromDishka[EnergyBalanceService],
    user: User = Depends(get_current_user),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    balances = await service.list_by_building(user, building_id, date_from, date_to)
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
