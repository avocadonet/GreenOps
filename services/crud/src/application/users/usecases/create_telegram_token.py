from domain.users.dtos import CreateTelegramTokenDto
from domain.users.entities import User
from domain.users.repositories import TelegramTokensRepository


class CreateTelegramTokenUseCase:
    """Кейс для генерации токена привязки Telegram-аккаунта.

    Создает уникальный токен для авторизации через Telegram бота
    и формирует ссылку для начала процесса привязки аккаунта.
    """

    def __init__(
        self,
        repository: TelegramTokensRepository,
    ):
        """Инициализирует кейс с репозиторием для работы с токенами."""

        self.__repository = repository

    async def __call__(self, bot_name: str, actor: User) -> str:
        """Генерирует токен и возвращает ссылку для привязки Telegram.

        Создает новый токен, привязанный к пользователю, и возвращает
        готовую ссылку для запуска Telegram-бота с этим токеном.
        """

        token = await self.__repository.create(CreateTelegramTokenDto(actor.id))
        return f"t.me/{bot_name}?start={token.id}"
