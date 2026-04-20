from uuid import UUID

from domain.users.entities import User
from domain.users.repositories import (
    UserActivationTokenRepository,
    UsersRepository,
)

from application.auth.tokens.dtos import TokenPairDto
from application.auth.usecases import CreateTokenPairUseCase
from application.transactions import TransactionsGateway
from application.users.usecases.read import ReadUserUseCase
from application.users.usecases.update import UpdateUserUseCase


class ValidateActivationTokenUseCase:
    """Кейс для валидации токена активации пользователя.

    Обеспечивает процесс активации учетной записи пользователя через токен,
    включая пометку токена как использованного, изменение статуса пользователя
    и генерацию новой пары токенов для авторизации.
    """

    def __init__(
        self,
        users_repository: UsersRepository,
        token_repository: UserActivationTokenRepository,
        read_user_use_case: ReadUserUseCase,
        tx: TransactionsGateway,
        create_token_pair_use_case: CreateTokenPairUseCase,
        update_user_use_case: UpdateUserUseCase,
    ):
        """Инициализирует зависимости для работы с пользователями,
        токенами активации и управления транзакциями.
        """

        self.__users_repository = users_repository
        self.__token_repository = token_repository
        self.__read_user_use_case = read_user_use_case
        self.__transaction = tx
        self.__create_token_pair_use_case = create_token_pair_use_case
        self.update_user_use_case = update_user_use_case

    async def __call__(self, token_uuid: UUID) -> tuple[User, TokenPairDto]:
        """Выполняет активацию пользователя по токену.

        Проверяет валидность токена, активирует учетную запись пользователя,
        помечает токен как использованный и возвращает пользователя с новой
        парой авторизационных токенов. Все операции выполняются атомарно.
        """

        async with self.__transaction:
            token = await self.__token_repository.read(token_uuid)
            await self.__token_repository.change_token_used_statement(token.id)
            await self.__users_repository.change_user_active_status(token.user.id, True)
            return token.user, await self.__create_token_pair_use_case(token.user)
