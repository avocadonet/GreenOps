from dishka import Provider, Scope, provide

from application.auth.tokens.config import TokenConfig
from application.auth.tokens.gateways import SecurityGateway, TokensGateway
from application.auth.usecases.authenticate import AuthenticateUseCase
from application.auth.usecases.authorize import AuthorizeUseCase
from application.auth.usecases.create_token_pair import CreateTokenPairUseCase
from application.auth.usecases.create_user_with_password import (
    CreateUserWithPasswordUseCase,
)
from application.auth.usecases.login import LoginUseCase
from domain.users.repositories import UsersRepository
from infrastructure.auth.bcrypt import BcryptSecurityGateway
from infrastructure.auth.jwt import JwtTokensGateway
from infrastructure.configs.config import Config
from infrastructure.db.users.repository import UsersDatabaseRepository


class AuthProvider(Provider):
    scope = Scope.REQUEST

    users_repository = provide(
        source=UsersDatabaseRepository, provides=UsersRepository
    )
    security_gateway = provide(
        source=BcryptSecurityGateway, provides=SecurityGateway
    )

    authenticate = provide(AuthenticateUseCase)
    authorize = provide(AuthorizeUseCase)
    create_token_pair = provide(CreateTokenPairUseCase)
    create_user_with_password = provide(CreateUserWithPasswordUseCase)
    login = provide(LoginUseCase)

    @provide(scope=Scope.APP)
    def get_token_config(self, config: Config) -> TokenConfig:
        return TokenConfig(secret_key=config.jwt_secret_key)

    @provide(scope=Scope.APP)
    def get_tokens_gateway(self, token_config: TokenConfig) -> TokensGateway:
        return JwtTokensGateway(token_config)
