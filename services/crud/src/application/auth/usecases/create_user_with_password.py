from domain.users.entities import User
from domain.users.repositories import UsersRepository

from ..dtos import CreateUserWithPasswordDto, RegisterUserDto
from ..tokens.gateways import SecurityGateway


class CreateUserWithPasswordUseCase:
    """
    Сценарий создания пользователя с защищенным паролем.

    Обеспечивает регистрацию нового пользователя с хешированием пароля
    и сохранением в системе. Создает неактивного пользователя,
    требующего подтверждения.
    """

    def __init__(
        self,
        users_repository: UsersRepository,
        security_gateway: SecurityGateway,
    ):
        """Инициализирует зависимости для регистрации пользователя."""

        self.__repository = users_repository
        self.__security_gateway = security_gateway

    async def __call__(self, dto: RegisterUserDto) -> User:
        """
        Выполняет процесс регистрации пользователя.

        Преобразует введенный пароль в защищенное представление,
        создает и сохраняет нового пользователя в системе.
        По умолчанию создается неактивный пользователь.
        """

        password_dto = self.__security_gateway.create_hashed_password(dto.password)
        dto = CreateUserWithPasswordDto(
            email=dto.email,
            fullname=dto.fullname,
            is_active=False,
            salt=password_dto.salt,
            hashed_password=password_dto.hashed_password,
        )

        return await self.__repository.create(dto)
