from domain.users.entities import User
from domain.users.repositories import UsersRepository

from application.transactions import TransactionsGateway

from .read import ReadUserUseCase


class DeleteUserUseCase:
    """Кейс для удаления учетной записи пользователя.

    Обеспечивает безопасное удаление пользователя из системы
    с проверкой прав доступа и сохранением целостности данных.
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

    async def __call__(self, actor: User) -> User:
        """Выполняет удаление учетной записи пользователя."""

        async with self.__transaction:
            user = await self.__read_user_use_case(actor.id)
            return await self.__repository.delete(user)
