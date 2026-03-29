class InvalidTransactionHandlingException(Exception):
    pass


class CrudxException(Exception):
    def __init__(self, message: str, **kwargs):
        super().__init__(f"{message} {kwargs}" if kwargs else message)


class NotFoundException(CrudxException):
    def __init__(self, **kwargs):
        super().__init__(f"Record not found", **kwargs)


class UniqueConstraintFailedException(CrudxException):
    def __init__(self, **kwargs):
        super().__init__(f"Unique constraint failed", **kwargs)


class DuplicateKeyException(CrudxException):
    def __init__(self, **kwargs):
        super().__init__(f"Duplicate entity", **kwargs)
