"""
Request ID middleware.

Injects a unique request identifier into every request so that all log
lines emitted during a single request share the same correlation ID.
This makes production debugging dramatically easier — grep for a single
ID to see the full lifecycle of a request across all log statements.

The ID is:
  - Read from the incoming X-Request-ID header (so upstream proxies / API
    gateways can set a trace ID that flows end-to-end).
  - Generated as a UUID4 when the header is absent.
  - Exposed on the response as X-Request-ID so clients can correlate too.
  - Stored in a context var so any logger can read it without threading it
    through every function call.

Usage
-----
Import REQUEST_ID_CTX_VAR in any module that needs the current request ID:

    from core.middleware.request_id import REQUEST_ID_CTX_VAR
    request_id = REQUEST_ID_CTX_VAR.get()

Or use the convenience helper:

    from core.middleware.request_id import get_request_id
    logger.info("Doing thing", extra={"request_id": get_request_id()})

The RequestIdFilter below injects the ID automatically into every log
record when attached to a handler — see logging setup in main.py.
"""

import logging
import uuid
from contextvars import ContextVar
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Module-level context var — survives across async awaits within the same task.
REQUEST_ID_CTX_VAR: ContextVar[str] = ContextVar("request_id", default="-")

REQUEST_ID_HEADER = "X-Request-ID"


def get_request_id() -> str:
    """Return the request ID for the current async context."""
    return REQUEST_ID_CTX_VAR.get()


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that ensures every request has a correlation ID.

    Order matters: add this before other middleware so the ID is available
    to all subsequent layers (rate limiting, auth, route handlers).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Store in context var so log filters can read it without
        # needing to pass the request object everywhere.
        token = REQUEST_ID_CTX_VAR.set(request_id)

        try:
            response = await call_next(request)
        finally:
            # Always reset — prevents ID leaking into the next request if
            # the event loop reuses the same task.
            REQUEST_ID_CTX_VAR.reset(token)

        response.headers[REQUEST_ID_HEADER] = request_id
        return response


class RequestIdFilter(logging.Filter):
    """
    Logging filter that injects `request_id` into every log record.

    Attach to a handler (not the logger) so it applies to all loggers
    that share the handler:

        handler.addFilter(RequestIdFilter())

    Then reference it in the log format:

        "%(levelname)s %(name)s [%(request_id)s] %(message)s"
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()  # type: ignore[attr-defined]
        return True
