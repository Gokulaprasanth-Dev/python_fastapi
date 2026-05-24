import logging
import logging.config
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.v1.router import v1_router
from core.config.settings import get_settings
from core.db.motor import database
from core.db.indexes import ensure_indexes
from core.exceptions.handlers import register_exception_handlers
from core.middleware.rate_limit import limiter
from core.middleware.request_id import RequestIdFilter, RequestIdMiddleware


def _configure_logging() -> None:
    """
    Configure structured logging with request ID injection.

    Every log line gets a [request_id] field so production log queries
    like `grep <uuid>` show the full lifecycle of a single request.
    The format is kept simple enough to ingest in most log aggregators
    (Datadog, CloudWatch, Loki) without extra parsing rules.
    """
    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s [%(request_id)s] %(message)s",
        handlers=[handler],
    )

    # Suppress noisy third-party loggers in production.
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await database.connect()
    await ensure_indexes(database.get_database())
    yield
    await database.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()

    _configure_logging()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Request ID must be first so all subsequent middleware and handlers
    # can read the correlation ID from the context var.
    app.add_middleware(RequestIdMiddleware)

    # Attach the rate-limiter state so slowapi can find it.
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # CORS — restrict to configured origins in non-local environments.
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

    # Trusted hosts — only enforce when a list is configured.
    if settings.trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

    register_exception_handlers(app)
    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
