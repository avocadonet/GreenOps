from application.auth.exceptions import InvalidCredentialsError
from application.auth.services import AuthService
from application.auth.tokens.gateways import TokensGateway
from dishka.integrations.fastapi import FromDishka, inject
from domain.users.entities import User
from fastapi import Header


@inject
async def get_current_user(
    authorization: str = Header(...),
    tokens: FromDishka[TokensGateway] = ...,
    auth: FromDishka[AuthService] = ...,
) -> User:
    if not authorization.startswith("Bearer "):
        raise InvalidCredentialsError("authorization header")
    token = authorization.removeprefix("Bearer ")
    token_info = await tokens.extract_token_info(token)
    return await auth.authorize(token_info)
