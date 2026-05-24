from typing import Protocol, Self

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession


class UnitOfWork(Protocol):
    """
    Abstract transaction boundary.

    Usage:
        async with uow:
            await repo.create(..., session=uow.session)
            await repo.create(..., session=uow.session)
        # commits on clean exit, rolls back on exception
    """

    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...

    @property
    def session(self) -> AsyncIOMotorClientSession | None: ...


class MongoUnitOfWork:
    """
    MongoDB-backed Unit of Work.

    Wraps motor's client session and transaction lifecycle.
    Commits automatically on clean context-manager exit.
    Aborts automatically if an exception is raised.

    IMPORTANT: Pass uow.session to every repository call inside the block,
    otherwise MongoDB will not enroll those writes in the transaction:

        async with uow:
            await company_repo.create_company(company, session=uow.session)
            await user_repo.create_user(user, session=uow.session)

    NOTE: Transactions require a MongoDB replica set or Atlas cluster.
    Standalone mongod instances will raise a server error at start_transaction().
    For local development without a replica set, set MONGO_TRANSACTIONS_ENABLED=false
    in your .env and the NoOpUnitOfWork will be used instead.
    """

    def __init__(self, client: AsyncIOMotorClient) -> None:
        self._client = client
        self._session: AsyncIOMotorClientSession | None = None

    @property
    def session(self) -> AsyncIOMotorClientSession | None:
        return self._session

    async def __aenter__(self) -> "MongoUnitOfWork":
        self._session = await self._client.start_session()
        self._session.start_transaction()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            await self._session.end_session()
            self._session = None

    async def commit(self) -> None:
        if self._session:
            await self._session.commit_transaction()

    async def rollback(self) -> None:
        if self._session:
            await self._session.abort_transaction()


class NoOpUnitOfWork:
    """
    No-op Unit of Work for environments where transactions are unavailable
    (e.g. standalone mongod in local dev without a replica set).

    Writes are NOT atomic. Use only in development.
    """

    def __init__(self) -> None:
        self._session = None

    @property
    def session(self) -> None:
        return None

    async def __aenter__(self) -> "NoOpUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass
