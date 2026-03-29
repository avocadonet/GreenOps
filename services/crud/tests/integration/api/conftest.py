import asyncio
import os
from json import loads
from re import split
from typing import Any, AsyncGenerator
from uuid import uuid4

import httpx
import pytest
from starlette import status
from testcontainers.compose import ComposeContainer, DockerCompose
from testcontainers.compose.compose import _ignore_properties  # noqa

from infrastructure.configs import BASE_PATH


class MyDockerCompose(DockerCompose):
    def start(self, project_name: str | None = "test-project") -> None:
        base_cmd = self.compose_command_property or []
        if self.pull:
            self._run_command(cmd=[*base_cmd, "pull"])
        up_cmd = [*base_cmd, "-p", project_name, "up"] if project_name else [*base_cmd, "up"]
        if self.build:
            up_cmd.append("--build")
        up_cmd.append("--wait" if self.wait else "--detach")
        if self.services:
            up_cmd.extend(self.services)
        self._run_command(cmd=up_cmd)
        if self._wait_strategies:
            for service, strategy in self._wait_strategies.items():
                strategy.wait_until_ready(self.get_container(service_name=service))

    def get_containers(
        self, include_all: bool = False, project_name: str | None = "test-project"
    ) -> list[ComposeContainer]:
        base = [*self.compose_command_property, "-p", project_name] if project_name else list(self.compose_command_property)
        cmd = [*base, "ps", "--format", "json"]
        if include_all:
            cmd.append("-a")
        result = self._run_command(cmd=cmd)
        stdout = split(r"\r?\n", result.stdout.decode("utf-8"))
        containers: list[ComposeContainer] = []
        for line in stdout:
            if not line:
                continue
            data = loads(line)
            if isinstance(data, list):
                containers += [_ignore_properties(ComposeContainer, d) for d in data]
            else:
                containers.append(_ignore_properties(ComposeContainer, data))
        for container in containers:
            container._docker_compose = self
        return containers


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def docker_compose():
    os.environ.update({
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_HOST": "core-postgres",
        "POSTGRES_PORT": "5432",
        "secret_key": "testing",
    })
    with MyDockerCompose(
        context=BASE_PATH / "../../",
        compose_file_name="docker-compose.yaml",
        build=True,
        env_file=None,
        wait=True,
        keep_volumes=False,
        services=["core-postgres", "crud-migrations", "svc-crud"],
    ) as compose:
        yield compose


@pytest.fixture(scope="session")
def database_url(docker_compose):
    port = docker_compose.get_service_port("core-postgres", 5432)
    return (
        f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@localhost:{port}/{os.getenv('POSTGRES_DB')}"
    )


@pytest.fixture(scope="session")
def crud_service_base_url(docker_compose):
    port = docker_compose.get_service_port("svc-crud", 5000)
    return f"http://localhost:{port}"


@pytest.fixture(scope="session")
async def client(crud_service_base_url) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=crud_service_base_url, timeout=120) as ac:
        while True:
            try:
                await ac.get("")
                break
            except (httpx.TimeoutException, httpx.RemoteProtocolError):
                await asyncio.sleep(0.1)
        yield ac


@pytest.fixture(scope="session")
def create_user_payload() -> dict[str, Any]:
    return {
        "email": f"{uuid4()}@example.com",
        "password": "StrongP@ssw0rd!",
        "orgId": str(uuid4()),
    }


@pytest.fixture(scope="session")
def login_payload(create_user_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "email": create_user_payload["email"],
        "password": create_user_payload["password"],
    }


@pytest.fixture(autouse=True)
async def registered_user(client: httpx.AsyncClient, create_user_payload):
    login = await client.post("/v1/auth/login", json=create_user_payload)
    if login.status_code == status.HTTP_200_OK:
        return {"user_with_token": login.json(), "cookies": login.cookies}

    registered = await client.post("/v1/auth/register", json=create_user_payload)
    assert registered.status_code == status.HTTP_200_OK, registered.text

    await asyncio.sleep(0.1)

    login = await client.post("/v1/auth/login", json=create_user_payload)
    assert login.status_code == status.HTTP_200_OK, login.text

    return {"user_with_token": login.json(), "cookies": login.cookies}


@pytest.fixture
async def access_token(registered_user):
    return registered_user["user_with_token"]["accessToken"]


@pytest.fixture
async def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}
