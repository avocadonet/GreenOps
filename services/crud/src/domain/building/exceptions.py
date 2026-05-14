from shared.exceptions import EntityAlreadyExistsException, EntityNotFoundException


class BuildingNotFoundException(EntityNotFoundException):
    def __init__(self, **kwargs):
        super().__init__("Building", **kwargs)


class BuildingAlreadyExistsException(EntityAlreadyExistsException):
    def __init__(self, **kwargs):
        super().__init__("Building", **kwargs)
