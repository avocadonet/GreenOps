from domain.users.dtos import CreateActivationTokenDto
from domain.users.entities import UserActivationToken
from domain.users.repositories import UserActivationTokenRepository


class CreateUserActivationTokenUseCase:
    """Кейс для создания токена активации пользователя.

    Генерирует и сохраняет уникальный токен, необходимый для подтверждения
    регистрации или активации учетной записи пользователя.
    """

    def __init__(self, repository: UserActivationTokenRepository):
        """Инициализирует кейс с репозиторием для работы с токенами активации."""

        self.__repository = repository

    async def __call__(self, dto: CreateActivationTokenDto) -> UserActivationToken:
        """Создает новый токен активации на основе переданных данных.

        Возвращает сгенерированный токен, который может быть использован
        для подтверждения действий пользователя в системе.
        """

        return await self.__repository.create(dto)
