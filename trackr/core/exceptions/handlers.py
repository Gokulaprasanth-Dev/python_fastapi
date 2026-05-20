from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.exceptions.base import ConflictError, NotFoundError, ValidationError
from modules.auth.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(request, exc: NotFoundError):  # type: ignore[no-untyped-def]
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ConflictError)
    async def _conflict(request, exc: ConflictError):  # type: ignore[no-untyped-def]
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ValidationError)
    async def _validation(request, exc: ValidationError):  # type: ignore[no-untyped-def]
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(InvalidCredentialsError)
    async def _invalid_credentials(request, exc: InvalidCredentialsError):  # type: ignore[no-untyped-def]
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(TokenExpiredError)
    async def _token_expired(request, exc: TokenExpiredError):  # type: ignore[no-untyped-def]
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(InvalidTokenError)
    async def _invalid_token(request, exc: InvalidTokenError):  # type: ignore[no-untyped-def]
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(TokenRevokedError)
    async def _token_revoked(request, exc: TokenRevokedError):  # type: ignore[no-untyped-def]
        return JSONResponse(status_code=401, content={"detail": str(exc)})
