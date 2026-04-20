from collections.abc import Callable

from application.auth.enums import PermissionsEnum
from application.auth.exceptions import InvalidCredentialsError
from application.auth.permissions.role_map import ROLE_PERMISSIONS
from application.auth.tokens.gateways import TokensGateway
from application.auth.usecases.authorize import AuthorizeUseCase
from dishka.integrations.fastapi import FromDishka, inject
from domain.users.entities import User
from fastapi import Depends, Header, HTTPException


@inject
async def get_current_user(
    authorization: str = Header(...),
    tokens: FromDishka[TokensGateway] = ...,
    authorize: FromDishka[AuthorizeUseCase] = ...,
) -> User:
    if not authorization.startswith("Bearer "):
        raise InvalidCredentialsError("authorization header")
    token = authorization.removeprefix("Bearer ")
    token_info = await tokens.extract_token_info(token)
    return await authorize(token_info)


def require_permission(perm: PermissionsEnum) -> Callable:
    async def check(user: User = Depends(get_current_user)) -> User:
        if perm not in ROLE_PERMISSIONS.get(user.role, set()):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return check
