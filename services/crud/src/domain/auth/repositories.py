from abc import ABCMeta, abstractmethod
from uuid import UUID

from domain.auth import entities
from domain.auth import dtos


class UsersRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create(self, dto: dtos.CreateUserDto) -> entities.User: ...

    @abstractmethod
    async def read(self, user_id: UUID) -> entities.User: ...

    @abstractmethod
    async def read_by_email(self, email: str) -> entities.User: ...

    @abstractmethod
    async def update(self, user: entities.User) -> entities.User: ...

    @abstractmethod
    async def delete(self, user: entities.User) -> entities.User: ...
