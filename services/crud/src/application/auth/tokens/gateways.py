from abc import ABCMeta, abstractmethod

from .dtos import PasswordDto, TokenInfoDto, TokenPairDto


class TokensGateway(metaclass=ABCMeta):
    """
    Абстрактный шлюз для работы с токенами аутентификации.
    Определяет интерфейс для генерации и верификации токенов.
    """

    @abstractmethod
    async def create_token_pair(self, subject: str) -> TokenPairDto: ...

    @abstractmethod
    async def extract_token_info(
        self, token: str, check_expires: bool = True
    ) -> TokenInfoDto: ...


class SecurityGateway(metaclass=ABCMeta):
    """
    Абстрактный шлюз для операций безопасности.
    Инкапсулирует логику работы с паролями и солями.
    """

    @abstractmethod
    def create_salt(self) -> str: ...

    @abstractmethod
    def create_hashed_password(self, password: str) -> PasswordDto: ...

    @abstractmethod
    def verify_passwords(
        self, plain_password: str, hashed_password: PasswordDto
    ) -> bool: ...
