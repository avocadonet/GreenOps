from domain.users.entities import User
from domain.users.exceptions import CalendarUUIDNotFoundError
from domain.users.repositories import UsersRepository


class DeleteCalendarLinkUseCase:
    """Кейс для удаления ссылки на подписку календаря пользователя.

    Отменяет ранее сгенерированную подписку на события пользователя,
    удаляя UUID календаря из настроек. Обеспечивает обработку случая
    отсутствия активной подписки.
    """

    def __init__(self, repository: UsersRepository):
        """Инициализирует кейс с репозиторием пользователей."""

        self.__repository = repository

    async def __call__(self, actor: User):
        """Удаляет UUID календаря из настроек пользователя.

        Если подписка активна (имеется calendar_uuid) - обнуляет его,
        в противном случае выбрасывает исключение CalendarUUIDNotFoundError.
        Возвращает обновленного пользователя при успешном выполнении.
        """

        if actor.settings.calendar_uuid is not None:
            actor.settings.calendar_uuid = None
            return await self.__repository.update(actor)
        raise CalendarUUIDNotFoundError
