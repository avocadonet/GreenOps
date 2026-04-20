from domain.users.entities import User
from domain.users.enums import UserNotificationSendToEnum
from domain.users.exceptions import TelegramNotConnectedError
from domain.users.repositories import UsersRepository

from application.transactions import TransactionsGateway
from application.users.dtos import UpdateUserDto
from application.users.usecases.read import ReadUserUseCase


class UpdateUserUseCase:
    """Кейс для обновления данных пользователя.

    Инкапсулирует логику изменения информации о пользователе,
    включая основные данные и интеграционные идентификаторы.
    Обеспечивает атомарность операций обновления.
    """

    def __init__(
        self,
        repository: UsersRepository,
        read_user_use_case: ReadUserUseCase,
        tx: TransactionsGateway,
    ):
        """Инициализирует зависимости для работы с пользователями,
        чтения данных и управления транзакциями.
        """

        self.__repository = repository
        self.__read_user_use_case = read_user_use_case
        self.__transaction = tx

    async def __call__(self, dto: UpdateUserDto, actor: User) -> User:
        """Обновляет данные пользователя."""

        async with self.__transaction:
            user = await self.__read_user_use_case(dto.user_id)
            if dto.fullname:
                user.fullname = dto.fullname
            if dto.telegram_id:
                user.telegram_id = dto.telegram_id
            if dto.send_to_type:
                if (
                    user.telegram_id is None
                    and dto.send_to_type == UserNotificationSendToEnum.TELEGRAM
                ):
                    raise TelegramNotConnectedError
                user.settings.type = dto.send_to_type

            return await self.__repository.update(user)
