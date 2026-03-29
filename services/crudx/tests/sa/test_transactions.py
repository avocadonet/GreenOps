import asyncio
from functools import partial
from unittest.mock import AsyncMock, Mock

import pytest
from crudx.exceptions import InvalidTransactionHandlingException
from crudx.sa.transaction import (
    AsyncDatabaseTransaction,
    AsyncTransactionsDatabaseGateway,
)
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction


def always_after_first():
    yield False
    while True:
        yield True


@pytest.mark.asyncio
async def test_commit_calls_underlying_transaction_commit():
    mock_transaction = AsyncMock(spec=AsyncSessionTransaction)
    transaction = AsyncDatabaseTransaction(mock_transaction)

    await transaction.commit()

    mock_transaction.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_rollback_calls_underlying_transaction_rollback():
    mock_transaction = AsyncMock(spec=AsyncSessionTransaction)
    transaction = AsyncDatabaseTransaction(mock_transaction)

    await transaction.rollback()

    mock_transaction.rollback.assert_awaited_once()


@pytest.fixture(name="mock_session")
def _mock_session():
    return Mock(spec=AsyncSession)


@pytest.fixture(name="mock_transaction")
def _mock_transaction():
    mock = AsyncMock(spec=AsyncSessionTransaction)

    async def _aexit_bound(self, exc_type, exc, tb):  # noqa
        if exc is None:
            await self.commit()
            return False
        else:
            await self.rollback()
            return False

    mock.__aexit__ = AsyncMock(side_effect=partial(_aexit_bound, mock))
    return mock


@pytest.fixture(name="mock_begin_cm")
def _mock_begin_cm(mock_transaction):
    cm = AsyncMock()
    cm.__aenter__.return_value = mock_transaction

    async def _cm_aexit(exc_type, exc, tb):
        return await mock_transaction.__aexit__(exc_type, exc, tb)

    cm.__aexit__ = AsyncMock(side_effect=_cm_aexit)
    return cm


@pytest.mark.asyncio
async def test_aenter_starts_transaction_returns_wrapper(
    mock_session, mock_begin_cm, mock_transaction
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction

    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    async with gateway as transaction:
        assert isinstance(transaction, AsyncDatabaseTransaction)

        mock_session.begin.assert_called_once()
        mock_begin_cm.__aenter__.assert_awaited_once()
        assert gateway._is_active

    mock_begin_cm.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_aexit_commits_on_success(mock_session, mock_begin_cm, mock_transaction):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction
    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    async with gateway:
        pass

    mock_transaction.commit.assert_awaited_once()
    mock_transaction.__aexit__.assert_awaited_once_with(None, None, None)
    assert not gateway._is_active


@pytest.mark.asyncio
async def test_aexit_rolls_back_on_exception(
    mock_session, mock_transaction, mock_begin_cm
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction
    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    with pytest.raises(Exception):
        async with gateway:
            raise Exception("Test exception")

    mock_transaction.rollback.assert_awaited_once()
    mock_transaction.__aexit__.assert_awaited_once()
    assert not gateway._is_active


@pytest.mark.asyncio
async def test_nested_creates_new_gateway_with_parent(
    mock_session, mock_transaction, mock_begin_cm
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction
    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    async with gateway:
        nested_gateway = gateway.nested()

        assert await nested_gateway._parent_transaction.__aenter__() == mock_transaction
        assert nested_gateway._is_nested is True
        assert nested_gateway._session == mock_session


@pytest.mark.asyncio
async def test_nested_raises_when_inactive(mock_session):
    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    with pytest.raises(InvalidTransactionHandlingException) as exc_info:
        gateway.nested()

    assert "Cannot create nested transaction from inactive gateway" in str(
        exc_info.value
    )


@pytest.mark.asyncio
async def test_nested_uses_savepoints(mock_session):
    mock_parent_transaction = AsyncMock(spec=AsyncSessionTransaction)
    mock_nested_transaction = AsyncMock(spec=AsyncSessionTransaction)
    mock_session.begin_nested.return_value = mock_nested_transaction

    gateway = AsyncTransactionsDatabaseGateway(
        mock_session, parent_transaction=mock_parent_transaction
    )

    async with gateway as transaction:
        assert isinstance(transaction, AsyncDatabaseTransaction)
        mock_session.begin_nested.assert_called_once()
        mock_nested_transaction.__aenter__.assert_awaited_once()


@pytest.mark.asyncio
async def test_aexit_inactive_raises_exception(mock_session):
    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    with pytest.raises(InvalidTransactionHandlingException) as exc_info:
        await gateway.__aexit__(None, None, None)

    assert "Transaction is not active" in str(exc_info.value)


@pytest.mark.asyncio
async def test_nested_transaction_creates_new_context(
    mock_session, mock_transaction, mock_begin_cm
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction

    mock_nested_transaction = AsyncMock(spec=AsyncSessionTransaction)
    mock_session.begin_nested.return_value = mock_nested_transaction

    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    async with gateway:
        nested_gateway = gateway.nested()
        async with nested_gateway as nested_transaction:
            # assert
            assert isinstance(nested_transaction, AsyncDatabaseTransaction)
            mock_session.begin_nested.assert_called_once()
            mock_nested_transaction.__aenter__.assert_awaited_once()


@pytest.mark.asyncio
async def test_multiple_nested_transactions(
    mock_session, mock_transaction, mock_begin_cm
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction

    mock_nested_transaction1 = AsyncMock(spec=AsyncSessionTransaction)
    mock_nested_transaction2 = AsyncMock(spec=AsyncSessionTransaction)
    mock_session.begin_nested.side_effect = [
        mock_nested_transaction1,
        mock_nested_transaction2,
    ]

    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    async with gateway:
        nested1 = gateway.nested()
        async with nested1:
            nested2 = nested1.nested()
            async with nested2:
                assert mock_session.begin_nested.call_count == 2


@pytest.mark.asyncio
async def test_auto_nested_on_reentrant_enter(
    mock_session, mock_transaction, mock_begin_cm
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction

    mock_nested_transaction = AsyncMock(spec=AsyncSessionTransaction)
    mock_session.begin_nested.return_value = mock_nested_transaction

    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    async with gateway:
        async with gateway as nested_transaction:
            assert isinstance(nested_transaction, AsyncDatabaseTransaction)
            mock_session.begin_nested.assert_called_once()


@pytest.mark.asyncio
async def test_auto_nested_on_reentrant_enter_more_times(
    mock_session, mock_transaction, mock_begin_cm
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction

    mock_nested_transaction = AsyncMock(spec=AsyncSessionTransaction)
    mock_session.begin_nested.return_value = mock_nested_transaction

    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    async with gateway:
        async with gateway:
            async with gateway as nested_transaction:
                assert isinstance(nested_transaction, AsyncDatabaseTransaction)
                assert mock_session.begin_nested.call_count == 2


@pytest.mark.asyncio
async def test_transaction_cleanup_on_exception(
    mock_session, mock_transaction, mock_begin_cm
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction

    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    try:
        async with gateway:
            raise ValueError("Test error")
    except ValueError:
        pass

    assert not gateway._is_active
    assert gateway._transaction is None


@pytest.mark.asyncio
async def test_lock_prevents_race_conditions(
    mock_session, mock_transaction, mock_begin_cm
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction

    async def enter_gateway():
        gateway = AsyncTransactionsDatabaseGateway(mock_session)
        async with gateway:
            await asyncio.sleep(0.01)
            return True

    results = await asyncio.gather(*[enter_gateway() for _ in range(5)])

    assert all(results)


@pytest.mark.asyncio
async def test_nested_gateway_inherits_session_properly(
    mock_session, mock_transaction, mock_begin_cm
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction
    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    async with gateway:
        nested_gateway = gateway.nested()

        assert nested_gateway._session == mock_session
        assert await nested_gateway._parent_transaction.__aenter__() == mock_transaction
        assert nested_gateway._is_nested is True


@pytest.mark.asyncio
async def test_transaction_wrapper_holds_correct_transaction(
    mock_session, mock_transaction, mock_begin_cm
):
    mock_session.begin.return_value = mock_begin_cm
    mock_session.in_transaction.side_effect = always_after_first()
    mock_session.get_transaction.return_value = mock_transaction
    gateway = AsyncTransactionsDatabaseGateway(mock_session)

    async with gateway as wrapper:
        assert isinstance(wrapper, AsyncDatabaseTransaction)
        assert await wrapper._transaction.__aenter__() == mock_transaction
