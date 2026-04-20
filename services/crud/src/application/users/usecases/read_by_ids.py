from domain.users.entities import User
from domain.users.repositories import UsersRepository


class ReadUsersByIdsUseCase:
    """Кейс для получения списка пользователей по их идентификаторам.

    Обеспечивает массовое чтение пользовательских данных по переданному списку ID.
    Используется для оптимизированной загрузки данных о группе пользователей.
    """

    def __init__(self, repository: UsersRepository):
        """Инициализирует кейс с репозиторием пользователей."""

        self.__repository = repository

    async def __call__(self, user_ids: list[int]) -> list[User]:
        """Возвращает список пользователей по указанным идентификаторам."""

        return await self.__repository.read_by_ids(user_ids)
