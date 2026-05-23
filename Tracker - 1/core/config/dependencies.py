from typing import Annotated

from fastapi import Depends

from core.config.settings import Settings, get_settings

# Inject settings as an explicit FastAPI dependency rather than calling
# get_settings() inline in route handlers or sub-dependencies. This makes
# the dependency graph visible in OpenAPI and easier to override in tests.
#
# Usage:
#   async def my_route(settings: AppSettings) -> ...:
#       if settings.mongo_transactions_enabled: ...

AppSettings = Annotated[Settings, Depends(get_settings)]
