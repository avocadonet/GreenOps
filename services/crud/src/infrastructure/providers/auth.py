from dishka import Provider, Scope, provide

from application.auth.services import AuthService
from application.auth.tokens.config import TokenConfig
from application.auth.tokens.gateways import SecurityGateway, TokensGateway
from domain.users.repositories import UsersRepository
from infrastructure.auth.bcrypt import BcryptSecurityGateway
from infrastructure.auth.jwt import JwtTokensGateway
from infrastructure.configs.config import Config
from infrastructure.db.users.repository import UsersDatabaseRepository


class AuthProvider(Provider):
    scope = Scope.REQUEST

    users_repository = provide(source=UsersDatabaseRepository, provides=UsersRepository)
    security_gateway = provide(source=BcryptSecurityGateway, provides=SecurityGateway)
    auth_service = provide(AuthService)

    @provide(scope=Scope.APP)
    def get_token_config(self, config: Config) -> TokenConfig:
        return TokenConfig(secret_key=config.jwt_secret_key)

    @provide(scope=Scope.APP)
    def get_tokens_gateway(self, token_config: TokenConfig) -> TokensGateway:
        return JwtTokensGateway(token_config)
