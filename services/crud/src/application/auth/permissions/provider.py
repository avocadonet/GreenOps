from abc import ABCMeta, abstractmethod

from application.auth.enums import PermissionsEnum


class PermissionProvider(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self) -> set[PermissionsEnum]: ...

    def org_scope(self) -> set[int] | None:
        """Org IDs this provider grants access to. None = unrestricted (global)."""
        return None
