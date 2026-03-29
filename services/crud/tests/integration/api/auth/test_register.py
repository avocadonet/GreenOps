from copy import copy
from uuid import uuid4

import httpx
import pytest
from starlette import status


@pytest.mark.anyio
async def test_register_happy_path(
    client: httpx.AsyncClient, create_user_payload: dict[str, str]
):
    payload = copy(create_user_payload)
    payload["email"] = f"{uuid4()}@example.com"

    response = await client.post("/v1/auth/register", json=payload)

    assert response.status_code == status.HTTP_200_OK, response.text


@pytest.mark.anyio
async def test_register_missing_payload_fields(client: httpx.AsyncClient):
    wrong_payloads = [{"email": "new@example.com"}, {"password": "<PASSWORD>"}]

    for wrong_payload in wrong_payloads:
        response = await client.post("/v1/auth/register", json=wrong_payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, (
            response.text
        )


@pytest.mark.anyio
async def test_register_wrong_email_format(
    client: httpx.AsyncClient, create_user_payload: dict[str, str]
):
    bad_email_user_payload = copy(create_user_payload)
    bad_email_user_payload["email"] = "<EMAIL>"

    response = await client.post("/v1/auth/register", json=bad_email_user_payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text


@pytest.mark.anyio
async def test_register_duplicate_email(
    client: httpx.AsyncClient, create_user_payload: dict[str, str]
):
    payload = copy(create_user_payload)
    payload["email"] = f"{uuid4()}@example.com"

    response = await client.post("/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_200_OK, response.text

    duplicated_response = await client.post("/v1/auth/register", json=payload)
    assert duplicated_response.status_code == status.HTTP_400_BAD_REQUEST, (
        duplicated_response.text
    )
