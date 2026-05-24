from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class UnitOfWork:
    """
    Abstract transaction boundary protocol.

    Usage:
        async with uow:
            await repo.create(..., session=uow.session)
        # commits on clean exit, rolls back on exception
    """

    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...

    @property
    def session(self) -> AsyncSession | None: ...


class PostgresUnitOfWork:
    """
    PostgreSQL-backed Unit of Work using SQLAlchemy AsyncSession.

    Commits automatically on clean context-manager exit.
    Rolls back automatically if an exception is raised.

    Pass uow.session to every repository call inside the block:

        async with uow:
            await company_repo.create_company(company, session=uow.session)
            await user_repo.create_user(user, session=uow.session)
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession | None:
        return self._session

    async def __aenter__(self) -> "PostgresUnitOfWork":
        self._session = self._session_factory()
        await self._session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            if self._session:
                await self._session.close()
            self._session = None

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()


class NoOpUnitOfWork:
    """
    No-op Unit of Work for unit tests — no real DB involved.
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
