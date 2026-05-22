from shared.schemas.base_schema import BaseSchema

from datetime import datetime,timezone

from pydantic import Field

class BlacklistedTokenModel(BaseSchema):
    id:str
    expires_at: datetime =Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )