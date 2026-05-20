from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from api.v1.router import v1_router
from core.config.settings import get_settings
from core.db.motor import database
# from core.exceptions.handlers import register_exception_handlers
# from core.middleware.request_id import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await database.connect()

    yield

    await database.disconnect()
    # s = get_settings()
    # await init_db(s.mongo_uri, s.mongo_db)  # 1. primary store first
    # yield
    # await shutdown_db()  # reverse order on shutdown
   

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # app.add_middleware(RequestIDMiddleware)
    # register_exception_handlers(app)
    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
