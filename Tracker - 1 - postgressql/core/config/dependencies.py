from typing import Annotated

from fastapi import Depends

from core.config.settings import Settings, get_settings

AppSettings = Annotated[Settings, Depends(get_settings)]
