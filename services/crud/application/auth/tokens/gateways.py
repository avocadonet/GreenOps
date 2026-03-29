from abc import ABCMeta, abstractmethod

from domain.auth.entities import User

from .dtos import TokenInfoDto, TokenPairDto


class TokensGateway(metaclass=ABCMeta):
    @abstractmethod
    async def create_token_pair(self, user: User) -> TokenPairDto: ...

    @abstractmethod
    async def extract_token_info(
        self, token: str, check_expires: bool = True
    ) -> TokenInfoDto: ...


class SecurityGateway(metaclass=ABCMeta):
    @abstractmethod
    def create_hashed_password(self, password: str) -> str: ...

    @abstractmethod
    def verify_passwords(self, plain_password: str, hashed_password: str) -> bool: ...
