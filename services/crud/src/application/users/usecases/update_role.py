from domain.users.entities import User, UserOrganizationRole
from domain.users.enums import RoleEnum, roles_delete_priorities_table
from domain.users.exceptions import UserAccessDenied
from domain.users.repositories import UserOrganizationRolesRepository
from domain.users.role_getter import RoleGetter

from application.auth.enums import PermissionsEnum
from application.auth.permissions import PermissionBuilder
from application.transactions import TransactionsGateway
from application.users.permissions.user import UserRolesPermissionProvider


class UpdateUserRoleUseCase:
    """Кейс для обновления роли пользователя в организации.

    Обеспечивает изменение организационных ролей с проверкой прав доступа
    и соблюдением иерархии привилегий. Все операции выполняются атомарно
    в рамках транзакции.
    """

    def __init__(
        self,
        repository: UserOrganizationRolesRepository,
        transaction: TransactionsGateway,
        permission_builder: PermissionBuilder,
        role_getter: RoleGetter,
    ):
        """Инициализирует зависимости для работы с ролями,
        управления транзакциями и проверки прав доступа.
        """

        self.__repository = repository
        self.__transaction = transaction
        self.__builder = permission_builder
        self.__role_getter = role_getter

    def __has_perms(self, role, actor_role):
        """Проверяет наличие прав на изменение роли.

        Учитывает иерархию ролей и специальные права супер-пользователя.
        Возвращает True, если текущий пользователь имеет достаточно прав
        для изменения указанной роли.
        """

        return (
            role.role != RoleEnum.OWNER or actor_role.role == RoleEnum.SUPER_USER
        ) and roles_delete_priorities_table[
            actor_role.role
        ] < roles_delete_priorities_table[role.role]

    async def __call__(
        self, entity: UserOrganizationRole, actor: User
    ) -> UserOrganizationRole:
        """Обновляет роль пользователя в организации.

        Проверяет права инициатора на изменение роли, валидирует
        соответствие иерархии привилегий и выполняет обновление.
        В случае отсутствия прав выбрасывает исключение UserAccessDenied.
        """

        async with self.__transaction:
            actor_role = await self.__role_getter(actor, entity.organization_id)
            self.__builder.providers(
                UserRolesPermissionProvider(entity.organization_id, actor_role)
            ).add(PermissionsEnum.CAN_UPDATE_ROLE).apply()
            if self.__has_perms(entity, actor_role):
                return await self.__repository.update(entity)
            raise UserAccessDenied
