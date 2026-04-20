from domain.users.entities import User, UserOrganizationRole
from domain.users.enums import RoleEnum, roles_delete_priorities_table
from domain.users.exceptions import UserAccessDenied
from domain.users.repositories import UserOrganizationRolesRepository
from domain.users.role_getter import RoleGetter

from application.auth.enums import PermissionsEnum
from application.auth.permissions import PermissionBuilder
from application.transactions import TransactionsGateway
from application.users.permissions.user import UserRolesPermissionProvider


class CreateUserRoleUseCase:
    """Кейс для создания новой роли пользователя в организации.

    Инкапсулирует бизнес-логику назначения ролей с проверкой прав доступа.
    Обеспечивает контроль иерархии ролей и ограничение привилегий.
    """

    def __init__(
        self,
        repository: UserOrganizationRolesRepository,
        permission_builder: PermissionBuilder,
        transaction: TransactionsGateway,
        role_getter: RoleGetter,
    ):
        """Инициализирует зависимости для работы с ролями,
        проверки прав и управления транзакциями.
        """

        self.__repository = repository
        self.__builder = permission_builder
        self.__transaction = transaction
        self.__role_getter = role_getter

    def __has_perms(self, role, actor_role):
        """Проверяет соответствие иерархии ролей.

        Определяет, имеет ли текущий пользователь право назначать указанную роль,
        учитывая приоритеты и специальные права супер-пользователя.
        """

        return (
            role.role != RoleEnum.OWNER or actor_role.role == RoleEnum.SUPER_USER
        ) and roles_delete_priorities_table[
            actor_role.role
        ] < roles_delete_priorities_table[role.role]

    async def __call__(
        self, role: UserOrganizationRole, actor: User
    ) -> UserOrganizationRole:
        """Создает новую роль пользователя в организации.

        Проверяет права инициатора, валидирует соответствие иерархии ролей
        и сохраняет новую роль в системе. Операция выполняется атомарно.
        """

        async with self.__transaction:
            actor_role = await self.__role_getter(actor, role.organization_id)
            self.__builder.providers(
                UserRolesPermissionProvider(role.organization_id, actor_role)
            ).add(PermissionsEnum.CAN_CREATE_ROLE).apply()
            if self.__has_perms(role, actor_role):
                return await self.__repository.create(role)
            raise UserAccessDenied
