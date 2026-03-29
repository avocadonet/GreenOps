from domain.auth.dtos import CreateUserDto
from domain.auth.entities import User
from domain.auth.exceptions import UserNotFoundException

from ..users.services import UsersService
from .dtos import AuthenticateUserDto, RegisterUserDto
from .exceptions import InvalidCredentialsException
from .tokens.dtos import TokenInfoDto, TokenPairDto
from .tokens.gateways import SecurityGateway, TokensGateway


class AuthService:
    def __init__(
        self,
        security_gateway: SecurityGateway,
        tokens_gateway: TokensGateway,
        users_service: UsersService,
    ):
        self._security_gateway = security_gateway
        self._tokens_gateway = tokens_gateway
        self._users_service = users_service

    async def register(self, dto: RegisterUserDto) -> tuple[User, TokenPairDto]:
        hashed_password = self._security_gateway.create_hashed_password(dto.password)
        user = await self._users_service.create(
            CreateUserDto(
                email=dto.email,
                hashed_password=hashed_password,
                org_id=dto.org_id,
                role=dto.role,
            )
        )
        return user, await self._tokens_gateway.create_token_pair(user)

    async def authenticate(self, dto: AuthenticateUserDto) -> tuple[User, TokenPairDto]:
        try:
            user = await self._users_service.read_by_email(dto.email)
            is_password_valid = self._security_gateway.verify_passwords(
                plain_password=dto.password,
                hashed_password=user.hashed_password,
            )
            if not is_password_valid:
                raise InvalidCredentialsException("password")
            return user, await self._tokens_gateway.create_token_pair(user)
        except UserNotFoundException:
            raise InvalidCredentialsException("email")

    async def authorize(self, dto: TokenInfoDto) -> tuple[User, TokenPairDto]:
        try:
            user = await self._users_service.read_by_email(dto.subject)
            return user, await self._tokens_gateway.create_token_pair(user)
        except UserNotFoundException:
            raise InvalidCredentialsException("email")
