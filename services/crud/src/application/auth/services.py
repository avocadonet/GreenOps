from domain.users.entities import User
from domain.users.exceptions import UserNotFoundError, UserNotValidated
from domain.users.repositories import UsersRepository

from .dtos import AuthenticateUserDto, CreateUserWithPasswordDto, RegisterUserDto
from .exceptions import InvalidCredentialsError
from .tokens.dtos import PasswordDto, TokenInfoDto, TokenPairDto
from .tokens.gateways import SecurityGateway, TokensGateway


class AuthService:
    def __init__(
        self,
        security_gateway: SecurityGateway,
        tokens_gateway: TokensGateway,
        users_repository: UsersRepository,
    ):
        self._security_gateway = security_gateway
        self._tokens_gateway = tokens_gateway
        self._users_repository = users_repository

    async def login(self, dto: AuthenticateUserDto) -> tuple[User, TokenPairDto]:
        try:
            user = await self._users_repository.read_by_email(dto.email)
            is_valid = self._security_gateway.verify_passwords(
                dto.password,
                PasswordDto(hashed_password=user.hashed_password, salt=user.salt),
            )
            if not is_valid:
                raise InvalidCredentialsError("password")
            return user, await self._tokens_gateway.create_token_pair(user)
        except UserNotFoundError:
            raise InvalidCredentialsError("email")

    async def register(self, dto: RegisterUserDto) -> User:
        password_dto = self._security_gateway.create_hashed_password(dto.password)
        create_dto = CreateUserWithPasswordDto(
            email=dto.email,
            fullname=dto.fullname,
            is_active=True, # TODO: add verification by email
            salt=password_dto.salt,
            hashed_password=password_dto.hashed_password,
        )
        return await self._users_repository.create(create_dto)

    async def authorize(self, dto: TokenInfoDto) -> User:
        try:
            user = await self._users_repository.read_by_email(dto.subject)
            if not user.is_active:
                raise UserNotValidated
            return user
        except UserNotFoundError:
            raise InvalidCredentialsError("email")
