from domain.users.entities import UserOrganizationRole
from domain.users.repositories import UserOrganizationRolesRepository


class ReadUserRolesUseCase:
    """Кейс для получения списка ролей пользователя в организациях.

    Обеспечивает чтение всех организационных ролей, назначенных конкретному пользователю.
    Возвращает полный перечень прав и членства пользователя в различных организациях.
    """

    def __init__(self, repository: UserOrganizationRolesRepository):
        """Инициализирует кейс с репозиторием организационных ролей."""

        self.__repository = repository

    async def __call__(self, user_id: int) -> list[UserOrganizationRole]:
        """Получает все роли пользователя в системе."""

        return await self.__repository.read_all(user_id)
