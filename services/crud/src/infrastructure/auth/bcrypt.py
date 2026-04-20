import base64
import os

from application.auth.tokens.dtos import PasswordDto
from application.auth.tokens.gateways import SecurityGateway
from passlib.context import CryptContext


class BcryptSecurityGateway(SecurityGateway):
    """Реализация шлюза безопасности с использованием bcrypt.

    Обеспечивает хеширование паролей и проверку их соответствия.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_salt(self) -> str:
        """Генерирует криптографическую соль для усиления хеширования."""

        return base64.b64encode(os.urandom(32)).decode("utf-8")

    def create_hashed_password(self, password: str) -> PasswordDto:
        """Создает хеш пароля с использованием соли."""

        salt = self.create_salt()
        return PasswordDto(
            hashed_password=self.pwd_context.hash(password + salt), salt=salt
        )

    def verify_passwords(
        self, plain_password: str, hashed_password: PasswordDto
    ) -> bool:
        """Проверяет соответствие введенного пароля сохраненному хешу."""

        return self.pwd_context.verify(
            plain_password + hashed_password.salt,
            hashed_password.hashed_password,
        )
