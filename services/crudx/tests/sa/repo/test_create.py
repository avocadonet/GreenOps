from typing import Callable

import pytest
from crudx.exceptions import UniqueConstraintFailedException
from sqlalchemy.exc import IntegrityError
from tests.conftest import User, make_user


@pytest.mark.asyncio
async def test_create_happy_path(repo, make_user: Callable[[], User]):
    user = make_user()
    saved = await repo.create(user)
    assert isinstance(saved, User)
    assert user == saved


@pytest.mark.asyncio
async def test_create_already_exists(repo, user: User):
    with pytest.raises(UniqueConstraintFailedException):
        await repo.create(user)
