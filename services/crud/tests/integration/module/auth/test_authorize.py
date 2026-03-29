import pytest
import pytest_asyncio
from application.auth.exceptions import InvalidCredentialsException
from application.auth.services import AuthService
from application.auth.tokens.dtos import TokenInfoDto, TokenPairDto
from application.auth.tokens.gateways import TokensGateway
from domain.auth.entities import User


@pytest_asyncio.fixture
async def token_pair_dto(
    created_user: User, tokens_gateway: TokensGateway
) -> TokenPairDto:
    return await tokens_gateway.create_token_pair(created_user)


@pytest_asyncio.fixture
async def token_info_dto(
    token_pair_dto: TokenPairDto, tokens_gateway: TokensGateway
) -> TokenInfoDto:
    return await tokens_gateway.extract_token_info(token_pair_dto.access_token)


@pytest.mark.asyncio
async def test_auth_service_authorize_happy_path(
    token_info_dto: TokenInfoDto, created_user: User, auth_service: AuthService
):
    authorized, _ = await auth_service.authorize(token_info_dto)

    assert authorized == created_user


@pytest.mark.asyncio
async def test_auth_service_authorize_wrong_email(
    token_info_dto: TokenInfoDto, created_user: User, auth_service: AuthService
):
    token_info_dto.subject = "<EMAIL>"

    with pytest.raises(InvalidCredentialsException):
        await auth_service.authorize(token_info_dto)
