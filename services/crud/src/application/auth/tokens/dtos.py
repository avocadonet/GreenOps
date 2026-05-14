from dataclasses import dataclass
from datetime import datetime


@dataclass
class TokenPairDto:
    """
    Пара токенов для аутентификации и обновления сессии.
    Содержит access-токен для авторизации запросов и refresh-токен для получения новой пары.
    """

    access_token: str
    refresh_token: str


@dataclass
class TokenInfoDto:
    """
    Информация о токене, включающая идентификатор пользователя и срок действия.
    Используется для верификации и обработки токенов.
    """

    subject: str
    expires_in: datetime


@dataclass
class PasswordDto:
    """
    Данные защищенного пароля, включающие хеш и соль.
    Обеспечивает безопасное хранение учетных данных пользователя.
    """

    hashed_password: str
    salt: str
