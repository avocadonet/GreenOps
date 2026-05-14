from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from application.auth.exceptions import InvalidCredentialsError
from domain.exceptions import EntityAccessDenied
from domain.sensor.exceptions import SensorAttachmentException
from domain.users.exceptions import UserAlreadyExistsError, UserNotValidated
from shared.exceptions import EntityNotFoundException


def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(EntityAccessDenied)
    async def access_denied_handler(request: Request, exc: EntityAccessDenied):
        return JSONResponse(status_code=403, content={"detail": f"Forbidden {exc}"})

    @app.exception_handler(EntityNotFoundException)
    async def not_found_handler(request: Request, exc: EntityNotFoundException):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(SensorAttachmentException)
    async def attachment_handler(request: Request, exc: SensorAttachmentException):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(InvalidCredentialsError)
    async def credentials_handler(request: Request, exc: InvalidCredentialsError):
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(UserNotValidated)
    async def not_validated_handler(request: Request, exc: UserNotValidated):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
