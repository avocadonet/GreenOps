from application.auth.services import AuthService
from application.users.services import UsersService
from dishka import Provider, Scope, provide


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    auth = provide(AuthService)
    users = provide(UsersService)
