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
        self._providers: list[tuple[PermissionProvider, set[PermissionsEnum]]] = []

    def providers(self, *providers: PermissionProvider) -> "PermissionBuilder":
        """Добавляет разрешения из переданных провайдеров."""

        for provider in providers:
            perms = provider()
            self._providers.append((provider, perms))
            self.permissions |= perms
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
        missing = self.necessary - self.permissions
        if missing:
            missing_str = ", ".join(p.value for p in missing)
            granted_str = ", ".join(p.value for p in self.permissions) or "none"
            raise EntityAccessDenied(
                f"missing=[{missing_str}], granted=[{granted_str}]"
            )

    def scope_for(self, perm: PermissionsEnum) -> set[int] | None:
        """Returns org IDs accessible for the given permission, None = unrestricted."""
        scope: set[int] = set()
        for provider, perms in self._providers:
            if perm in perms:
                provider_scope = provider.org_scope()
                if provider_scope is None:
                    return None
                scope |= provider_scope
        return scope
