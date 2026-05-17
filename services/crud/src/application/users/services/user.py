from domain.users.dtos import ReadAllUsersDto
from domain.users.entities import User
from domain.users.enums import UserNotificationSendToEnum
from domain.users.exceptions import TelegramNotConnectedError
from domain.users.repositories import UsersRepository
from domain.users.role_getter import RoleGetter

from application.auth.enums import PermissionsEnum
from application.auth.permissions.builder import PermissionBuilder
from application.auth.permissions.user_provider import UserPermissionProvider
from application.transaction import TransactionsGateway
from application.users.dtos import UpdateUserDto
from application.organization.service import OrganizationService
from application.users.services.role import UserRoleService


class UserService:
    def __init__(
        self,
        repository: UsersRepository,
        tx: TransactionsGateway,
        role_getter: RoleGetter,
        organization_service: OrganizationService,
        roles_service: UserRoleService,
    ):
        self._repository = repository
        self._tx = tx
        self._role_getter = role_getter
        self._organization_service = organization_service
        self._roles_service = roles_service

    def _check(self, user: User, *perms: PermissionsEnum) -> None:
        PermissionBuilder().providers(UserPermissionProvider(user)).add(*perms).apply()

    async def get(self, user_id: int, actor: User = None) -> User:
        if actor and user_id != actor.id:
            self._check(actor, PermissionsEnum.CAN_READ_ROLE)
        return await self._repository.read(user_id)

    async def list_all(self, dto: ReadAllUsersDto, actor: User) -> list[User]:
        if actor.role.value.startswith("SUPER"):
            self._check(actor, PermissionsEnum.CAN_READ_ROLE)
            return await self._repository.read_all(dto)

        async with self._tx:
            organizations = await self._organization_service.list_all(
                actor, 1, 10000
            )  # костыль хе
            roles = []
            for org in organizations:
                roles.extend(
                    await self._roles_service.read_all_by_organization_id(org.id)
                )

            user_ids = [role.user_id for role in roles]
            return await self.get_by_ids(user_ids)

    async def get_by_ids(self, user_ids: list[int]) -> list[User]:
        return await self._repository.read_by_ids(user_ids)

    async def update(self, dto: UpdateUserDto, actor: User) -> User:
        async with self._tx:
            user = await self.get(dto.user_id)
            if dto.fullname:
                user.fullname = dto.fullname
            if dto.telegram_id:
                user.telegram_id = dto.telegram_id
            if dto.send_to_type:
                if (
                    user.telegram_id is None
                    and dto.send_to_type == UserNotificationSendToEnum.TELEGRAM
                ):
                    raise TelegramNotConnectedError
                user.settings.type = dto.send_to_type
            return await self._repository.update(user)

    async def delete(self, actor: User) -> User:
        async with self._tx:
            user = await self.get(actor.id)
            return await self._repository.delete(user)
