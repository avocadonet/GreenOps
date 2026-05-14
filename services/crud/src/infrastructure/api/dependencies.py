from application.auth.services import AuthService
from application.auth.tokens.gateways import TokensGateway
from dishka.integrations.fastapi import FromDishka, inject
from domain.users.entities import User
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

http_bearer = HTTPBearer()


@inject
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    tokens: FromDishka[TokensGateway] = ...,
    auth: FromDishka[AuthService] = ...,
) -> User:
    token_info = await tokens.extract_token_info(credentials.credentials)
    return await auth.authorize(token_info)
