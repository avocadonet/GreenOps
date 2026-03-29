import httpx
import pytest
from starlette import status


@pytest.fixture
async def refresh_cookie(client, login_payload, registered_user):
    return registered_user["cookies"]


@pytest.mark.anyio
async def test_refresh_happy_path(
    client: httpx.AsyncClient,
    registered_user,
):
    response = await client.post("/v1/auth/refresh", cookies=registered_user["cookies"])

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["user"] == registered_user["user_with_token"]["user"]


@pytest.mark.anyio
async def test_refresh_missing_cookie(client: httpx.AsyncClient):
    client.cookies.clear()

    response = await client.post("/v1/auth/refresh")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text


@pytest.mark.anyio
async def test_refresh_tampered_cookie(client):
    response = await client.post(
        "/v1/auth/refresh", cookies={"refresh": "definitely-invalid"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
