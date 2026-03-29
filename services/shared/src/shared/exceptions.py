class GreenOpsException(Exception):
    pass


class EntityNotFoundException(GreenOpsException):
    def __init__(self, entity_name: str, **kwargs):
        super().__init__(f"{entity_name} not found: {kwargs}")
        self.entity_name = entity_name
        self.params = kwargs


class EntityAlreadyExistsException(GreenOpsException):
    def __init__(self, entity_name: str, **kwargs):
        super().__init__(f"{entity_name} already exists: {kwargs}")
        self.entity_name = entity_name
        self.params = kwargs
