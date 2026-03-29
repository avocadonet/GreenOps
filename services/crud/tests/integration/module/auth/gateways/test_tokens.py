from datetime import timedelta

import pytest
from application.auth.exceptions import InvalidCredentialsException
from application.auth.tokens.config import TokenConfig
from application.auth.tokens.gateways import TokensGateway
from domain.auth.entities import User


@pytest.mark.asyncio
async def test_tokens_gateway_happy_path(
    tokens_gateway: TokensGateway, created_user: User
):
    token_pair = await tokens_gateway.create_token_pair(created_user)

    access_token_info = await tokens_gateway.extract_token_info(token_pair.access_token)
    refresh_token_info = await tokens_gateway.extract_token_info(
        token_pair.refresh_token
    )

    for token in [access_token_info, refresh_token_info]:
        assert token.subject == created_user.email
        assert token.user_id == created_user.user_id


@pytest.mark.asyncio
async def test_tokens_gateway_invalid_token(tokens_gateway: TokensGateway):
    with pytest.raises(InvalidCredentialsException):
        await tokens_gateway.extract_token_info("invalid token")


@pytest.mark.asyncio
async def test_tokens_gateway_tokens_expired(
    tokens_gateway: TokensGateway, created_user: User, monkeypatch
):
    monkeypatch.setattr(
        tokens_gateway,
        "_config",
        TokenConfig(
            secret_key="secret",
            access_token_expires_time=timedelta(seconds=0),
            refresh_token_expires_time=timedelta(seconds=0),
        ),
    )
    token_pair = await tokens_gateway.create_token_pair(created_user)

    with pytest.raises(InvalidCredentialsException):
        await tokens_gateway.extract_token_info(token_pair.access_token)
    with pytest.raises(InvalidCredentialsException):
        await tokens_gateway.extract_token_info(token_pair.refresh_token)
