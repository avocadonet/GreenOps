from application.auth.exceptions import InvalidCredentialsException
from crudx import exceptions
from domain.exceptions import EntityAccessDeniedException
from domain.auth.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


async def _entity_not_found_exception_handler(
    _: Request, exc: exceptions.NotFoundException | UserNotFoundException
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)},
    )


async def _entity_already_exists_exception_handler(
    _: Request, exc: UserAlreadyExistsException
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)},
    )


async def _entity_access_denied_handler(_: Request, exc: EntityAccessDeniedException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"message": str(exc)},
    )


async def _invalid_credentials_exception_handler(
    _: Request, exc: InvalidCredentialsException
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": str(exc)},
    )


def register_exceptions_handlers(app: FastAPI) -> None:
    paths = (
        (exceptions.NotFoundException, _entity_not_found_exception_handler),
        (UserNotFoundException, _entity_not_found_exception_handler),
        (UserAlreadyExistsException, _entity_already_exists_exception_handler),
        (EntityAccessDeniedException, _entity_access_denied_handler),
        (InvalidCredentialsException, _invalid_credentials_exception_handler),
    )

    for path, handler in paths:
        app.add_exception_handler(path, handler)
