from shared.exceptions import EntityAlreadyExistsException, EntityNotFoundException


class UnitNotFoundException(EntityNotFoundException):
    def __init__(self, **kwargs):
        super().__init__("Unit", **kwargs)


class UnitAlreadyExistsException(EntityAlreadyExistsException):
    def __init__(self, **kwargs):
        super().__init__("Unit", **kwargs)
