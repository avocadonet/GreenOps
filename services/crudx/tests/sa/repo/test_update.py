from typing import Callable

import pytest
from crudx.exceptions import NotFoundException
from tests.conftest import User, make_user


@pytest.mark.asyncio
async def test_update_happy_path(repo, user: User):
    user.fullname = "new fullname"
    updated = await repo.update(user)

    assert isinstance(updated, User)
    assert updated == user


@pytest.mark.asyncio
async def test_update_non_existent(repo, make_user: Callable[[], User]):
    new_user = make_user()
    new_user.fullname = "new fullname"

    with pytest.raises(NotFoundException):
        await repo.update(new_user)
