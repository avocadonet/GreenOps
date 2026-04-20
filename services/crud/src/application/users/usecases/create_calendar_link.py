from uuid import uuid4

from domain.users.entities import User
from domain.users.repositories import UsersRepository


class CreateCalendarLinkUseCase:
    """Кейс для генерации ссылки на подписку на календарь пользователя.

    Создает уникальную ссылку для подписки на события пользователя
    в формате iCalendar. Генерирует новый UUID для календаря при первом обращении.
    """

    def __init__(self, repository: UsersRepository):
        """Инициализирует кейс с репозиторием пользователей."""

        self.__repository = repository

    async def __call__(self, base_url: str, actor: User) -> str:
        """Создает или возвращает существующую ссылку для подписки на календарь.

        Генерирует новый идентификатор календаря при отсутствии,
        сохраняет его в настройках пользователя и возвращает полную ссылку.
        """

        if actor.settings.calendar_uuid is None:
            uuid = uuid4()
            actor.settings.calendar_uuid = uuid
            await self.__repository.update(actor)
        else:
            uuid = actor.settings.calendar_uuid
        return f"{base_url}/v1/events/subscribe/ical/{uuid}"
