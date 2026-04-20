from dataclasses import dataclass


@dataclass
class AuthenticateUserDto:
    """
    Данные для аутентификации пользователя.
    Содержит email и пароль для входа в систему.
    """

    email: str
    password: str


@dataclass
class RegisterUserDto:
    """
    Данные для регистрации нового пользователя.
    Включает основные учетные данные и флаг активности.
    """

    email: str
    password: str
    fullname: str = ""
    is_active: bool = False


@dataclass
class CreateUserWithPasswordDto:
    """
    Данные для создания пользователя с защищенным паролем.
    """

    email: str
    fullname: str
    is_active: bool
    salt: str
    hashed_password: str
