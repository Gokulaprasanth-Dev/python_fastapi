import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class Database:
    """
    PostgreSQL async connection manager using SQLAlchemy 2.x.

    Handles:
    - engine creation and connection pool
    - session factory
    - graceful shutdown
    """

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        self.engine = create_async_engine(
            settings.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=settings.debug,
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        # Verify connectivity
        async with self.engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))

        logger.info("PostgreSQL connected successfully")

    async def disconnect(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
        logger.info("PostgreSQL connection closed")

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self.session_factory is None:
            raise RuntimeError(
                "Database not connected. "
                "Ensure application startup completed."
            )
        return self.session_factory

    def get_engine(self) -> AsyncEngine:
        if self.engine is None:
            raise RuntimeError(
                "Database not connected. "
                "Ensure application startup completed."
            )
        return self.engine


database = Database()


async def get_db_session() -> AsyncSession:
    """
    FastAPI dependency that yields an AsyncSession per request.
    Session is committed on success and rolled back on error.
    """
    factory = database.get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
