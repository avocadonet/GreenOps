from domain.exceptions import EntityAccessDenied

from application.auth.enums import PermissionsEnum
from application.auth.permissions.provider import PermissionProvider


class PermissionBuilder:
    """
    Строитель для проверки и применения прав доступа.

    Позволяет собирать разрешения из провайдеров и проверять
    наличие необходимых прав перед выполнением операции.
    """

    def __init__(self):
        """Инициализирует наборы разрешений и необходимых прав."""

        self.permissions = set()
        self.necessary = set()

    def providers(self, *providers: PermissionProvider) -> "PermissionBuilder":
        """Добавляет разрешения из переданных провайдеров."""

        for provider in providers:
            self.permissions |= provider()
        return self

    def add(self, *args: PermissionsEnum) -> "PermissionBuilder":
        """Добавляет необходимые права для проверки."""

        self.necessary |= set(args)
        return self

    def apply(self):
        """
        Проверяет, что все необходимые права присутствуют.

        Вызывает исключение `EntityAccessDenied`, если проверка не пройдена.
        """
        if not self.necessary <= self.permissions:
            raise EntityAccessDenied()
