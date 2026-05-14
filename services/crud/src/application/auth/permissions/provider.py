from abc import ABCMeta, abstractmethod

from application.auth.enums import PermissionsEnum


class PermissionProvider(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self) -> set[PermissionsEnum]: ...
