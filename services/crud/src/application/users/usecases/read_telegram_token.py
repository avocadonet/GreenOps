from uuid import UUID

from domain.users.entities import TelegramToken
from domain.users.repositories import TelegramTokensRepository


class ReadTelegramTokenUseCase:
    """Кейс для получения токена привязки Telegram.

    Обеспечивает чтение информации о токене авторизации Telegram
    по его уникальному идентификатору. Используется в процессе
    верификации и связывания аккаунтов.
    """

    def __init__(
        self,
        repository: TelegramTokensRepository,
    ):
        """Инициализирует кейс с репозиторием токенов Telegram."""

        self.__repository = repository

    async def __call__(self, token_id: UUID) -> TelegramToken:
        """Получает токен привязки Telegram по ID."""

        return await self.__repository.read(token_id)
