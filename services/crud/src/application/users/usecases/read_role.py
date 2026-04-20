from domain.users.entities import UserOrganizationRole
from domain.users.exceptions import UserRoleNotFoundError
from domain.users.repositories import UserOrganizationRolesRepository


class ReadUserRoleUseCase:
    """Кейс для получения роли пользователя в конкретной организации.

    Обеспечивает чтение информации о правах и уровне доступа пользователя
    в рамках определенной организации. Используется для проверки и управления
    организационными разрешениями.
    """

    def __init__(self, repository: UserOrganizationRolesRepository):
        """Инициализирует кейс с репозиторием организационных ролей."""

        self.__repository = repository

    async def __call__(
        self, user_id: int, organization_id: int
    ) -> UserOrganizationRole:
        """Получает роль пользователя в указанной организации."""

        return await self.__repository.read(user_id, organization_id)
