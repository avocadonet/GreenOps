from typing import Any

import httpx
import pytest
from starlette import status


@pytest.mark.anyio
async def test_login_happy_path(
    client: httpx.AsyncClient,
    registered_user: dict[str, Any],
    login_payload: dict[str, str],
):
    response = await client.post("/v1/auth/login", json=login_payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"] == registered_user["user_with_token"]["user"]


@pytest.mark.anyio
async def test_login_missing_fields(client: httpx.AsyncClient):
    wrong_payloads = [{"email": "new@example.com"}, {"password": "<PASSWORD>"}]

    for wrong_payload in wrong_payloads:
        response = await client.post("/v1/auth/login", json=wrong_payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, (
            response.text
        )


@pytest.mark.anyio
async def test_login_wrong_password(
    client: httpx.AsyncClient, registered_user, create_user_payload
):
    wrong_password_payload = {
        "email": create_user_payload["email"],
        "password": "totally-wrong",
    }

    response = await client.post("/v1/auth/login", json=wrong_password_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
