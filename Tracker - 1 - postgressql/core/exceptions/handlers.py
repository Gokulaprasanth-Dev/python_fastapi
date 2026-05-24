import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions.base import DomainError
from core.middleware.request_id import get_request_id

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        """Handles all business/domain exceptions."""
        logger.warning(
            "Domain error occurred",
            extra={
                "request_id": get_request_id(),
                "path": request.url.path,
                "method": request.method,
                "error_code": exc.error_code,
                "details": exc.details,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handles unexpected server errors."""
        logger.exception(
            "Unexpected server error",
            extra={
                "request_id": get_request_id(),
                "path": request.url.path,
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Something went wrong",
                }
            },
        )
