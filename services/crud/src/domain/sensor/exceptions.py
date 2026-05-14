from shared.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    GreenOpsException,
)


class SensorNotFoundException(EntityNotFoundException):
    def __init__(self, **kwargs):
        super().__init__("Sensor", **kwargs)


class SensorAlreadyExistsException(EntityAlreadyExistsException):
    def __init__(self, **kwargs):
        super().__init__("Sensor", **kwargs)


class SensorAttachmentException(GreenOpsException):
    """Raised when sensor attachment XOR constraint is violated."""
