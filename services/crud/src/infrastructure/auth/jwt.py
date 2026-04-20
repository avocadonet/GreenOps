from datetime import datetime, timedelta, timezone

import jwt
from application.auth.exceptions import InvalidCredentialsError
from application.auth.tokens.config import TokenConfig
from application.auth.tokens.dtos import TokenInfoDto, TokenPairDto
from application.auth.tokens.gateways import TokensGateway


class JwtTokensGateway(TokensGateway):
    """Реализация шлюза для работы с JWT токенами.

    Обеспечивает создание и верификацию пар access/refresh токенов.
    """

    def __init__(self, config: TokenConfig):
        """Инициализирует шлюз с конфигурацией токенов."""

        self.__config = config

    def __encode(self, subject: str, expires_time: timedelta | None = None) -> str:
        """Внутренний метод для кодирования JWT токена."""

        payload = {"sub": subject} | (
            {"exp": datetime.now(tz=timezone.utc) + expires_time}
            if expires_time
            else dict()
        )
        return jwt.encode(
            payload,
            key=self.__config.secret_key,
            algorithm=self.__config.algorithm,
        )

    async def create_token_pair(self, subject: str) -> TokenPairDto:
        """Генерирует пару access и refresh токенов для указанного субъекта."""

        access_token = self.__encode(subject, self.__config.access_token_expires_time)
        refresh_token = self.__encode(subject, self.__config.refresh_token_expires_time)
        return TokenPairDto(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def extract_token_info(
        self, token: str, check_expires: bool = True
    ) -> TokenInfoDto:
        """Извлекает информацию из токена и проверяет его валидность."""

        try:
            payload = jwt.decode(
                token,
                key=self.__config.secret_key,
                algorithms=[self.__config.algorithm],
                options={"verify_signature": check_expires},
            )
        except jwt.ExpiredSignatureError:
            raise InvalidCredentialsError()
        except jwt.DecodeError:
            raise InvalidCredentialsError()

        return TokenInfoDto(
            subject=payload["sub"],
            expires_in=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
