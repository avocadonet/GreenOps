from shared.exceptions import EntityAlreadyExistsException, EntityNotFoundException


class OrganizationNotFoundException(EntityNotFoundException):
    def __init__(self, **kwargs):
        super().__init__("Organization", **kwargs)


class OrganizationAlreadyExistsException(EntityAlreadyExistsException):
    def __init__(self, **kwargs):
        super().__init__("Organization", **kwargs)
