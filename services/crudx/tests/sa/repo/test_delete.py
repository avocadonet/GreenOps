from uuid import uuid4

import pytest
from crudx.exceptions import NotFoundException
from tests.conftest import User


@pytest.mark.asyncio
async def test_delete_happy_path(repo, user: User):
    result = await repo.delete(user)

    assert user == result


@pytest.mark.asyncio
async def test_delete_non_existent(repo, user: User):
    user.id = uuid4()

    with pytest.raises(NotFoundException):
        await repo.delete(user)
