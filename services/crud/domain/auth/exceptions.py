from domain.exceptions import EntityAlreadyExistsException, EntityNotFoundException
from domain.auth.entities import User


class UserNotFoundException(EntityNotFoundException):
    def __init__(self, **params):
        super().__init__(User, **params)


class UserAlreadyExistsException(EntityAlreadyExistsException):
    def __init__(self, **params):
        super().__init__(User, **params)
