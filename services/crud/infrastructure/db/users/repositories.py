from uuid import UUID

from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from crudx.sa.utils import from_query
from domain.auth import dtos, entities
from domain.auth.dtos import CreateUserDto
from domain.auth.entities import User
from domain.auth.exceptions import UserAlreadyExistsException, UserNotFoundException
from domain.auth.repositories import UsersRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import mappers
from .models import UserDatabaseModel


def params_maker(*args, **kwargs) -> dict:
    return kwargs | {
        f"{arg.__class__.__name__}_arg_{i}": arg for i, arg in enumerate(args)
    }


@provide(
    SqlalchemyConfig[dtos.CreateUserDto, User, UserDatabaseModel](
        create_mapper=mappers.user__create_mapper,
        entity_mapper=mappers.user__map_to_db,
        model_mapper=mappers.user__map_from_db,
        model=UserDatabaseModel,
        not_found=lambda *args, **kwargs: UserNotFoundException(
            **params_maker(*args, **kwargs)
        ),
        unique_constraint_failed=lambda *args, **kwargs: UserAlreadyExistsException(
            **params_maker(*args, **kwargs)
        ),
    )
)
class UsersDatabaseRepository(
    UsersRepository,
    ErrorHandlingSqlAlchemyRepository[CreateUserDto, User, UserDatabaseModel],
):
    def __init__(self, session: AsyncSession):
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=UserDatabaseModel, id_attr="user_id"
        )

    @decorators.read
    async def read(self, user_id: UUID) -> entities.User: ...

    @decorators.read
    async def read_by_email(self, email: str) -> entities.User:
        return from_query(
            select(self.config.model).where(self.config.model.email == email)
        )

    @decorators.create
    async def create(self, dto: dtos.CreateUserDto) -> entities.User: ...

    @decorators.update
    async def update(self, user: entities.User) -> entities.User: ...

    @decorators.delete
    async def delete(self, user: entities.User) -> entities.User: ...
