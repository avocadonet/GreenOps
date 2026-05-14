from shared.exceptions import (
    GreenOpsException,
    EntityAccessDeniedException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from domain.users.entities import TelegramToken, User, UserOrganizationRole


class UserNotFoundError(EntityNotFoundException):
    def __init__(self):
        super().__init__(User)


class UserAlreadyExistsError(EntityAlreadyExistsException):
    def __init__(self):
        super().__init__(User)


class UserAccessDenied(EntityAccessDeniedException):
    def __init__(self):
        super().__init__()


class UserNotValidated(GreenOpsException):
    def __init__(self):
        super().__init__(f"Пользователь не активирован!")


class TelegramTokenNotFoundError(EntityNotFoundException):
    def __init__(self):
        super().__init__(TelegramToken)


class TelegramTokenAlreadyExistsError(EntityAlreadyExistsException):
    def __init__(self):
        super().__init__(TelegramToken)


class UserRoleAlreadyExistsError(EntityAlreadyExistsException):
    def __init__(self):
        super().__init__(UserOrganizationRole)


class UserRoleNotFoundError(EntityNotFoundException):
    def __init__(self):
        super().__init__(UserOrganizationRole)


class CalendarUUIDNotFoundError(EntityNotFoundException):
    def __init__(self):
        super().__init__(User)


class TelegramNotConnectedError(GreenOpsException):
    def __init__(self):
        super().__init__("Telegram not connected")
