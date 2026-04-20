from domain.users.entities import User

from application.auth.tokens.dtos import TokenPairDto

from ..dtos import AuthenticateUserDto
from .authenticate import AuthenticateUseCase
from .create_token_pair import CreateTokenPairUseCase


class LoginUseCase:
    """
    Сценарий входа пользователя в систему.

    Объединяет процессы аутентификации и генерации токенов,
    предоставляя единый интерфейс для авторизации пользователей.
    """

    def __init__(
        self,
        authenticate_user_use_case: AuthenticateUseCase,
        create_token_pair_use_case: CreateTokenPairUseCase,
    ):
        """Инициализирует зависимости для процесса входа."""

        self.authenticate_user_use_case = authenticate_user_use_case
        self.create_token_pair_use_case = create_token_pair_use_case

    async def __call__(self, dto: AuthenticateUserDto) -> tuple[User, TokenPairDto]:
        """
        Выполняет полный процесс авторизации пользователя.

        Проверяет учетные данные и возвращает аутентифицированного пользователя
        вместе с новой парой токенов для доступа к системе.
        """

        user = await self.authenticate_user_use_case(dto)
        return user, await self.create_token_pair_use_case(user)
