from domain.users.entities import User

from application.auth.tokens.dtos import TokenPairDto
from application.auth.tokens.gateways import TokensGateway


class CreateTokenPairUseCase:
    """
    Сценарий создания пары токенов для пользователя.

    Генерирует новую пару access и refresh токенов
    для аутентификации и обновления сессии.
    """

    def __init__(self, tokens_gateway: TokensGateway):
        """Инициализирует шлюз для работы с токенами."""

        self.tokens_gateway = tokens_gateway

    async def __call__(self, user: User) -> TokenPairDto:
        """
        Создает пару токенов для указанного пользователя.

        Использует email пользователя в качестве subject для генерации токенов.
        """

        return await self.tokens_gateway.create_token_pair(user.email)
