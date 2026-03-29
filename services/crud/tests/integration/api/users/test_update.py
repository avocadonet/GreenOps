import httpx
import pytest
from starlette import status


@pytest.fixture(scope="session")
def update_me_payload() -> dict:
    return {"isActive": False}


@pytest.mark.anyio
async def test_update_happy_path(
    client: httpx.AsyncClient, auth_headers, update_me_payload
):
    response = await client.put(
        "/v1/users/me", json=update_me_payload, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["isActive"] == update_me_payload["isActive"]


@pytest.mark.anyio
async def test_update_wrong_payload(client: httpx.AsyncClient, auth_headers):
    response = await client.put(
        "/v1/users/me", json={"someWrongField": "value"}, headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.anyio
async def test_update_unauthorized(client: httpx.AsyncClient, update_me_payload):
    response = await client.put("/v1/users/me", json=update_me_payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
