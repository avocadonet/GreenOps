import asyncio
from typing import Optional

from crudx.exceptions import InvalidTransactionHandlingException
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction


class AsyncDatabaseTransaction:
    def __init__(self, transaction: AsyncSessionTransaction):
        self._transaction = transaction

    async def commit(self):
        await self._transaction.commit()

    async def rollback(self):
        await self._transaction.rollback()


class AsyncTransactionsDatabaseGateway:
    def __init__(
        self,
        session: AsyncSession,
        parent_transaction: Optional[AsyncSessionTransaction] = None,
    ):
        self._session = session
        self._parent_transaction = parent_transaction
        self._is_nested = parent_transaction is not None
        self._transaction: Optional[AsyncSessionTransaction] = None
        self._is_active = False
        self._lock = asyncio.Lock()
        self._stack = []

    async def __aenter__(self) -> AsyncDatabaseTransaction:
        if self._is_active:
            self._stack.append(self.nested())
            return await self._stack[-1].__aenter__()

        async with self._lock:
            in_tx = self._session.in_transaction()

            if in_tx:
                if self._is_nested and self._parent_transaction is not None:
                    self._transaction = self._session.begin_nested()
                    await self._transaction.__aenter__()
                else:
                    self._transaction = self._session.get_transaction()
            else:
                self._transaction = self._session.begin()
                await self._transaction.__aenter__()

            self._is_active = True

        return AsyncDatabaseTransaction(self._transaction)

    def nested(self) -> "AsyncTransactionsDatabaseGateway":
        """
        Тут немного сложно поэтому описание принципа работы:
        async with gateway as tx1:
            async with gateway as tx2:
                # tx2 is nested transaction for tx1
                async with gateway as tx3:
                    # tx3 is nested transaction for tx2, so it nested for tx1
                    pass

            async with gateway as tx3:
                # tx3 is not anyhow related with tx2
                pass
        """

        if not self._is_active:
            raise InvalidTransactionHandlingException(
                "Cannot create nested transaction from inactive gateway"
            )

        if self._stack:
            return AsyncTransactionsDatabaseGateway(
                self._session,
                parent_transaction=self._stack[-1]._transaction,  # noqa
            )
        return AsyncTransactionsDatabaseGateway(
            self._session, parent_transaction=self._transaction
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._stack:
            return await self._stack.pop().__aexit__(exc_type, exc_val, exc_tb)

        if not self._is_active:
            raise InvalidTransactionHandlingException("Transaction is not active")

        async with self._lock:
            try:
                await self._transaction.__aexit__(exc_type, exc_val, exc_tb)
            finally:
                self._is_active = False
                self._transaction = None
