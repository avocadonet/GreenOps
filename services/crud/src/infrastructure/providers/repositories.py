from dishka import Provider, Scope, provide
from domain.auth.repositories import UsersRepository

from infrastructure.db.users.repositories import UsersDatabaseRepository


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST
    users_repository = provide(source=UsersDatabaseRepository, provides=UsersRepository)
