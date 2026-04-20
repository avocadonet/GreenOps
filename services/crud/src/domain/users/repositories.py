from abc import ABCMeta, abstractmethod
from uuid import UUID

from application.auth.dtos import CreateUserWithPasswordDto

import domain.users.dtos as dtos
import domain.users.entities as entities
from domain.users.dtos import CreateActivationTokenDto, ReadAllUsersDto
from domain.users.entities import (
    User,
    UserActivationToken,
    UserOrganizationRole,
)


class UsersRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create(self, dto: CreateUserWithPasswordDto) -> User: ...

    @abstractmethod
    async def read(self, user_id: int) -> User: ...

    @abstractmethod
    async def read_by_email(self, email: str) -> User: ...

    @abstractmethod
    async def read_all(self, dto: ReadAllUsersDto) -> list[User]: ...

    @abstractmethod
    async def read_by_ids(
        self,
        user_ids: list[int],
    ) -> list[User]: ...

    @abstractmethod
    async def read_by_calendar_uuid(self, uuid: UUID) -> User: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user: User) -> User: ...

    @abstractmethod
    async def change_user_active_status(self, user_id: int, status: bool): ...

    @abstractmethod
    async def get_super_user(self) -> User: ...


class UserOrganizationRolesRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create(self, role: UserOrganizationRole) -> UserOrganizationRole: ...

    @abstractmethod
    async def read(
        self, user_id: int, organization_id: int
    ) -> UserOrganizationRole: ...

    @abstractmethod
    async def update(self, role: UserOrganizationRole) -> UserOrganizationRole: ...

    @abstractmethod
    async def delete(self, role: UserOrganizationRole) -> UserOrganizationRole: ...

    @abstractmethod
    async def read_all(self, user_id: int) -> list[UserOrganizationRole]: ...


class UserActivationTokenRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create(self, dto: CreateActivationTokenDto) -> UserActivationToken: ...

    @abstractmethod
    async def read(self, token_uuid: UUID) -> UserActivationToken: ...

    @abstractmethod
    async def change_token_used_statement(self, token_id: UUID): ...

    @abstractmethod
    async def delete(self, token: UserActivationToken) -> UserActivationToken: ...


class TelegramTokensRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create(
        self, dto: dtos.CreateTelegramTokenDto
    ) -> entities.TelegramToken: ...

    @abstractmethod
    async def read(self, token_id: UUID) -> entities.TelegramToken: ...

    @abstractmethod
    async def update(self, token: entities.TelegramToken) -> entities.TelegramToken: ...
