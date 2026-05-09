from fastapi import FastAPI

from infrastructure.api.auth.router import router as auth_router
from infrastructure.api.building.router import router as buildings_router
from infrastructure.api.energy_balance.router import router as energy_balances_router
from infrastructure.api.organization.router import router as organizations_router
from infrastructure.api.sensor.router import router as sensors_router
from infrastructure.api.threshold.router import router as thresholds_router
from infrastructure.api.unit.router import router as units_router

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter



def include_routers(app: FastAPI) -> None:
    api_router = APIRouter(prefix="/api", route_class=DishkaRoute)

    v1_router = APIRouter(prefix="/v1", route_class=DishkaRoute)

    v1_router.include_router(auth_router)
    v1_router.include_router(organizations_router)
    v1_router.include_router(buildings_router)
    v1_router.include_router(units_router)
    v1_router.include_router(sensors_router)
    v1_router.include_router(thresholds_router)
    v1_router.include_router(energy_balances_router)

    api_router.include_router(v1_router)

    app.include_router(api_router)
