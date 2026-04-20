from uuid import UUID

from domain.users.entities import User
from domain.users.repositories import UsersRepository


class ReadByCalendarUUIDUseCase:
    """Кейс для получения пользователя по UUID календаря.

    Обеспечивает поиск пользователя по уникальному идентификатору,
    связанному с подпиской на календарь событий. Используется для
    верификации доступа к ICS-календарю пользователя.
    """

    def __init__(self, repository: UsersRepository):
        """Инициализирует кейс с репозиторием пользователей."""

        self.__repository = repository

    async def __call__(self, uuid: UUID) -> User:
        """Находит пользователя по UUID календаря."""

        return await self.__repository.read_by_calendar_uuid(uuid)
