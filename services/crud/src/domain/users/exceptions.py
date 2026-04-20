from domain.exceptions import (
    EntityAccessDenied,
    EntityAlreadyExistsError,
    EntityException,
    EntityNotFoundError,
)
from domain.users.entities import TelegramToken, User, UserOrganizationRole


class UserNotFoundError(EntityNotFoundError):
    def __init__(self):
        super().__init__(User)


class UserAlreadyExistsError(EntityAlreadyExistsError):
    def __init__(self):
        super().__init__(User)


class UserAccessDenied(EntityAccessDenied):
    def __init__(self):
        super().__init__()


class UserNotValidated(EntityException):
    def __init__(self):
        super().__init__(f"Пользователь не активирован!")


class TelegramTokenNotFoundError(EntityNotFoundError):
    def __init__(self):
        super().__init__(TelegramToken)


class TelegramTokenAlreadyExistsError(EntityAlreadyExistsError):
    def __init__(self):
        super().__init__(TelegramToken)


class UserRoleAlreadyExistsError(EntityAlreadyExistsError):
    def __init__(self):
        super().__init__(UserOrganizationRole)


class UserRoleNotFoundError(EntityNotFoundError):
    def __init__(self):
        super().__init__(UserOrganizationRole)


class CalendarUUIDNotFoundError(EntityNotFoundError):
    def __init__(self):
        super().__init__(User)


class TelegramNotConnectedError(EntityException):
    def __init__(self):
        super().__init__("Telegram not connected")
