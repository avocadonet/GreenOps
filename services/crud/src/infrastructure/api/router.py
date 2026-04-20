from fastapi import FastAPI

from infrastructure.api.auth.router import router as auth_router
from infrastructure.api.building.router import router as buildings_router
from infrastructure.api.energy_balance.router import router as energy_balances_router
from infrastructure.api.sensor.router import router as sensors_router
from infrastructure.api.threshold.router import router as thresholds_router
from infrastructure.api.unit.router import router as units_router


def include_routers(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(buildings_router)
    app.include_router(units_router)
    app.include_router(sensors_router)
    app.include_router(thresholds_router)
    app.include_router(energy_balances_router)
