from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from application.auth.exceptions import InvalidCredentialsException
from application.auth.tokens.config import TokenConfig
from application.auth.tokens.dtos import TokenInfoDto, TokenPairDto
from application.auth.tokens.gateways import TokensGateway
from domain.auth.entities import User


class JwtTokensGateway(TokensGateway):
    def __init__(self, config: TokenConfig):
        self._config = config

    def _encode(self, user: User, expires_time: timedelta | None = None) -> str:
        payload = {
            "sub": user.email,
            "user_id": str(user.user_id),
            "exp": datetime.now(tz=timezone.utc) + expires_time,
        }
        return jwt.encode(
            payload,
            key=self._config.secret_key,
            algorithm=self._config.algorithm,
        )

    async def create_token_pair(self, user: User) -> TokenPairDto:
        access_token = self._encode(user, self._config.access_token_expires_time)
        refresh_token = self._encode(user, self._config.refresh_token_expires_time)
        return TokenPairDto(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def extract_token_info(
        self, token: str, check_expires: bool = True
    ) -> TokenInfoDto:
        try:
            payload = jwt.decode(
                token,
                key=self._config.secret_key,
                algorithms=[self._config.algorithm],
                options={"verify_signature": check_expires},
            )
        except jwt.ExpiredSignatureError:
            raise InvalidCredentialsException()
        except jwt.DecodeError:
            raise InvalidCredentialsException()

        return TokenInfoDto(
            subject=payload["sub"],
            user_id=UUID(payload["user_id"]),
            expires_in=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
