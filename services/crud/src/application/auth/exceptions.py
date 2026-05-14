class InvalidCredentialsError(Exception):
    """
    Исключение, возникающее при неверных учетных данных.

    Указывает на ошибку аутентификации с возможностью
    уточнения конкретного поля с неверными данными.
    """

    def __init__(self, field: str = None):
        default = "Invalid credentials were provide"
        message = field and f"Invalid credentials were provide at field={field}"
        super().__init__(message or default)
