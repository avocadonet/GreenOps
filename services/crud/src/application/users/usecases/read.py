from domain.users.entities import User
from domain.users.repositories import UsersRepository


class ReadUserUseCase:
    """Кейс для получения данных пользователя.

    Обеспечивает чтение информации о пользователе по его идентификатору.
    Возвращает полную модель данных пользователя.
    """

    def __init__(self, repository: UsersRepository):
        """Инициализирует кейс с репозиторием пользователей."""

        self.__repository = repository

    async def __call__(self, user_id: int) -> User:
        """Получает данные пользователя по ID.

        Возвращает объект пользователя или вызывает исключение,
        если пользователь не найден.
        """

        return await self.__repository.read(user_id)
