import uuid

import pytest
from sqlalchemy import update

from shared.db.user import UserModel
from tests.e2e.conftest import auth


class TestRegister:
    async def test_success(self, client):
        email = f"reg_{uuid.uuid4().hex[:8]}@test.local"
        r = await client.post("/auth/register", json={"email": email, "password": "Pass1234!", "fullname": "New User"})
        assert r.status_code == 201
        body = r.json()
        assert body["email"] == email
        assert "user_id" in body
        assert "message" in body

    async def test_duplicate_email_returns_409(self, client, admin):
        r = await client.post(
            "/auth/register",
            json={"email": admin["email"], "password": "Pass1234!", "fullname": "Dup"},
        )
        assert r.status_code == 409

    async def test_invalid_email_returns_422(self, client):
        r = await client.post("/auth/register", json={"email": "not-an-email", "password": "Pass1234!"})
        assert r.status_code == 422


class TestLogin:
    async def test_success_returns_tokens(self, client, admin):
        r = await client.post("/auth/login", json={"email": admin["email"], "password": "E2eTest1234!"})
        assert r.status_code == 200
        body = r.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["email"] == admin["email"]

    async def test_wrong_password_returns_401(self, client, admin):
        r = await client.post("/auth/login", json={"email": admin["email"], "password": "WrongPassword!"})
        assert r.status_code == 401

    async def test_unknown_email_returns_401(self, client):
        r = await client.post("/auth/login", json={"email": "nobody@nowhere.test", "password": "Pass1234!"})
        assert r.status_code == 401

    async def test_inactive_user_returns_403(self, client, db):
        email = f"inactive_{uuid.uuid4().hex[:8]}@test.local"
        r = await client.post("/auth/register", json={"email": email, "password": "Pass1234!", "fullname": "Inactive"})
        assert r.status_code == 201
        # Do NOT activate — user is inactive by default
        r = await client.post("/auth/login", json={"email": email, "password": "Pass1234!"})
        assert r.status_code == 403


class TestProtectedAccess:
    async def test_no_token_returns_422(self, client):
        r = await client.get("/buildings/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 422

    async def test_invalid_token_returns_401(self, client):
        r = await client.get(
            "/buildings/00000000-0000-0000-0000-000000000000",
            headers=auth("invalid.token.here"),
        )
        assert r.status_code == 401

    async def test_public_user_denied_on_buildings(self, client, public_user):
        r = await client.post(
            "/buildings",
            json={"address": "Forbidden St", "building_type": "RESIDENTIAL", "total_area": 10.0},
            headers=auth(public_user["token"]),
        )
        assert r.status_code == 403
