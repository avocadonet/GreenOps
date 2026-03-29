from shared.exceptions import EntityAlreadyExistsException, EntityNotFoundException


class ThresholdNotFoundException(EntityNotFoundException):
    def __init__(self, **kwargs):
        super().__init__("Threshold", **kwargs)


class ThresholdAlreadyExistsException(EntityAlreadyExistsException):
    def __init__(self, **kwargs):
        super().__init__("Threshold", **kwargs)
