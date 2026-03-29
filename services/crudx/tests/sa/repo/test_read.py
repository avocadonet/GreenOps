from uuid import uuid4

import pytest
from crudx.exceptions import NotFoundException
from tests.conftest import User

all_paths = pytest.mark.parametrize(
    "method",
    [
        lambda repo: repo.read,
        lambda repo: repo.read_from_dto,
        lambda repo: repo.read_from_query,
    ],
)


@pytest.mark.asyncio
@all_paths
async def test_read_happy_path(repo, user: User, method):
    saved = await method(repo)(id=user.id, email=user.email)

    assert saved == user


@pytest.mark.asyncio
@all_paths
async def test_read_wrong_params(repo, method):
    wrong_user_id = uuid4()
    wrong_user_email = f"{wrong_user_id}@e.com"
    with pytest.raises(NotFoundException):
        await method(repo)(id=wrong_user_id, email=wrong_user_email)


@pytest.mark.asyncio
@all_paths
async def test_read_wrong_id_type(repo, method):
    wrong_user_id = 42
    wrong_user_email = 42
    with pytest.raises(NotFoundException):
        await method(repo)(id=wrong_user_id, email=wrong_user_email)
