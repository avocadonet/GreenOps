import pytest
from starlette import status


@pytest.mark.anyio
async def test_delete_happy_path(client, registered_user, auth_headers):
    response = await client.delete("/v1/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_delete_unauthorized(client):
    response = await client.delete("/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_delete_several_times(client, auth_headers):
    response = await client.delete("/v1/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    duplicated = await client.delete("/v1/users/me", headers=auth_headers)
    assert duplicated.status_code == status.HTTP_401_UNAUTHORIZED
