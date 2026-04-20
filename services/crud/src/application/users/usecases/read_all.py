from domain.users.dtos import ReadAllUsersDto
from domain.users.entities import User
from domain.users.repositories import UsersRepository


class ReadAllUsersUseCase:
    """Кейс для получения списка пользователей с фильтрацией.

    Предоставляет функционал для чтения списка пользователей системы
    с возможностью пагинации, сортировки и фильтрации по заданным параметрам.
    """

    def __init__(self, repository: UsersRepository):
        """Инициализирует кейс с репозиторием пользователей."""

        self.__repository = repository

    async def __call__(self, dto: ReadAllUsersDto) -> list[User]:
        """Возвращает список пользователей согласно параметрам фильтрации."""

        return await self.__repository.read_all(dto)
