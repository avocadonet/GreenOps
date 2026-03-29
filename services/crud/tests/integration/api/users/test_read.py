import httpx
import pytest
from starlette import status


@pytest.mark.anyio
async def test_read_happy_path(
    client: httpx.AsyncClient, registered_user, auth_headers
):
    response = await client.get("/v1/users/me", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == registered_user["user_with_token"]["user"]


@pytest.mark.anyio
async def test_read_unauthorized(client):
    response = await client.get("/v1/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
