from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.building.exceptions import BuildingNotFoundException
from domain.sensor.exceptions import SensorAttachmentException, SensorNotFoundException
from domain.threshold.exceptions import ThresholdNotFoundException
from domain.unit.exceptions import UnitNotFoundException
from shared.exceptions import EntityNotFoundException


def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(EntityNotFoundException)
    async def not_found_handler(request: Request, exc: EntityNotFoundException):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(SensorAttachmentException)
    async def attachment_handler(request: Request, exc: SensorAttachmentException):
        return JSONResponse(status_code=422, content={"detail": str(exc)})
