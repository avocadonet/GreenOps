from uuid import UUID

from domain.users.dtos import CreateActivationTokenDto, CreateTelegramTokenDto
from domain.users.entities import TelegramToken, User, UserActivationToken
from domain.users.exceptions import TelegramTokenNotFoundError, UserAccessDenied
from domain.users.repositories import (
    TelegramTokensRepository,
    UserActivationTokenRepository,
    UsersRepository,
)

from application.auth.tokens.dtos import TokenPairDto
from application.auth.tokens.gateways import TokensGateway
from application.transaction import TransactionsGateway


class UserTokenService:
    def __init__(
        self,
        users_repository: UsersRepository,
        activation_token_repository: UserActivationTokenRepository,
        telegram_token_repository: TelegramTokensRepository,
        tx: TransactionsGateway,
        tokens_gateway: TokensGateway,
    ):
        self._users_repository = users_repository
        self._activation_token_repository = activation_token_repository
        self._telegram_token_repository = telegram_token_repository
        self._tx = tx
        self._tokens_gateway = tokens_gateway

    async def create_activation_token(self, dto: CreateActivationTokenDto) -> UserActivationToken:
        return await self._activation_token_repository.create(dto)

    async def validate_activation_token(self, token_uuid: UUID) -> tuple[User, TokenPairDto]:
        async with self._tx:
            token = await self._activation_token_repository.read(token_uuid)
            await self._activation_token_repository.change_token_used_statement(token.id)
            await self._users_repository.change_user_active_status(token.user.id, True)
            return token.user, await self._tokens_gateway.create_token_pair(token.user)

    async def create_telegram_token(self, bot_name: str, actor: User) -> str:
        token = await self._telegram_token_repository.create(CreateTelegramTokenDto(actor.id))
        return f"t.me/{bot_name}?start={token.id}"

    async def get_telegram_token(self, token_id: UUID) -> TelegramToken:
        return await self._telegram_token_repository.read(token_id)

    async def connect_telegram(self, token_id: UUID, telegram_id: int) -> None:
        async with self._tx.nested():
            try:
                token = await self.get_telegram_token(token_id)
            except TelegramTokenNotFoundError:
                raise UserAccessDenied
            user = await self._users_repository.read(token.user_id)
            user.telegram_id = telegram_id
            await self._users_repository.update(user)
            token.is_used = True
            await self._telegram_token_repository.update(token)
