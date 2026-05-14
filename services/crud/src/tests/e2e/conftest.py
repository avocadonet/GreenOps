import os
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://greenops:greenops@localhost:5432/greenops"
)
os.environ.setdefault("JWT_SECRET_KEY", "test-e2e-secret")

from infrastructure.api.app import create_app  # noqa: E402
from shared.db.user import UserModel  # noqa: E402


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest_asyncio.fixture(scope="session")
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest_asyncio.fixture(scope="session")
async def db():
    engine = create_async_engine(os.environ["DATABASE_URL"])
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()


async def _register_and_activate(client, db, role: str = "PUBLIC") -> dict:
    email = f"e2e_{uuid.uuid4().hex[:10]}@test.local"
    password = "E2eTest1234!"
    r = await client.post(
        "/auth/register",
        json={"email": email, "password": password, "fullname": "E2E User"},
    )
    assert r.status_code == 201, r.text
    user_id = r.json()["user_id"]
    await db.execute(
        update(UserModel)
        .where(UserModel.id == user_id)
        .values(is_active=True, role=role)
    )
    await db.commit()
    r = await client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"user_id": user_id, "email": email, "token": r.json()["access_token"]}


@pytest_asyncio.fixture(scope="session")
async def admin(client, db):
    user = await _register_and_activate(client, db, role="ADMIN")
    yield user
    # cascade deletes via user delete are not set up, so just mark inactive
    await db.execute(
        update(UserModel).where(UserModel.id == user["user_id"]).values(is_active=False)
    )
    await db.commit()


@pytest_asyncio.fixture(scope="session")
async def public_user(client, db):
    user = await _register_and_activate(client, db, role="PUBLIC")
    yield user
    await db.execute(
        update(UserModel).where(UserModel.id == user["user_id"]).values(is_active=False)
    )
    await db.commit()


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── shared resource fixtures ──────────────────────────────────────────────────


@pytest_asyncio.fixture
async def building(client, admin):
    r = await client.post(
        "/buildings",
        json={
            "address": "E2E Ave 1",
            "building_type": "RESIDENTIAL",
            "total_area": 200.0,
        },
        headers=auth(admin["token"]),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    yield data
    await client.delete(
        f"/buildings/{data['building_id']}", headers=auth(admin["token"])
    )


@pytest_asyncio.fixture
async def unit(client, admin, building):
    r = await client.post(
        "/units",
        json={
            "building_id": building["building_id"],
            "unit_number": "42A",
            "floor": 3,
            "owner_name": "Test Owner",
        },
        headers=auth(admin["token"]),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    yield data
    await client.delete(f"/units/{data['unit_id']}", headers=auth(admin["token"]))


@pytest_asyncio.fixture
async def common_sensor(client, admin, building):
    r = await client.post(
        "/sensors",
        json={
            "serial_number": f"SN-{uuid.uuid4().hex[:8]}",
            "model": "E2E Model",
            "calibration_date": "2024-01-01",
            "sensor_type": "COMMON",
            "building_id": building["building_id"],
        },
        headers=auth(admin["token"]),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    yield data
    await client.delete(f"/sensors/{data['sensor_id']}", headers=auth(admin["token"]))
