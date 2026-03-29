from application.auth.tokens.gateways import SecurityGateway, TokensGateway
from dishka import Provider, Scope, provide

from infrastructure.gateways.auth import BcryptSecurityGateway, JwtTokensGateway


class GatewaysProvider(Provider):
    scope = Scope.APP

    tokens_gateway = provide(source=JwtTokensGateway, provides=TokensGateway)
    security_gateway = provide(source=BcryptSecurityGateway, provides=SecurityGateway)
