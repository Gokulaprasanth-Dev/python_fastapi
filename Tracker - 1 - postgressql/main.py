import asyncio
import logging
import logging.config
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.v1.router import v1_router
from core.config.settings import get_settings
from core.db.postgres import database, get_db_session
from core.exceptions.handlers import register_exception_handlers
from core.middleware.rate_limit import limiter
from core.middleware.request_id import RequestIdFilter, RequestIdMiddleware


def _configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s [%(request_id)s] %(message)s",
        handlers=[handler],
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def _token_cleanup_task(interval_seconds: int = 3600) -> None:
    """
    Background task: purge expired tokens from token_blacklist every hour.
    Replaces the MongoDB TTL index.
    """
    from sqlalchemy import delete
    from core.db.tables.token_blacklist_table import TokenBlacklistTable

    logger = logging.getLogger(__name__)
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            factory = database.get_session_factory()
            async with factory() as session:
                result = await session.execute(
                    delete(TokenBlacklistTable).where(
                        TokenBlacklistTable.expires_at < datetime.now(timezone.utc)
                    )
                )
                await session.commit()
                logger.info("Token cleanup: removed %d expired tokens", result.rowcount)
        except Exception:
            logger.exception("Token cleanup task failed")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await database.connect()
    cleanup_task = asyncio.create_task(_token_cleanup_task())
    yield
    cleanup_task.cancel()
    await database.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()
    _configure_logging()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(RequestIdMiddleware)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    if settings.cors_allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    elif settings.environment == "local":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    if settings.trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

    register_exception_handlers(app)
    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
