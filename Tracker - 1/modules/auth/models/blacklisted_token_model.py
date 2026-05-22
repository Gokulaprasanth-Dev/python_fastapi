from shared.schemas.base_schema import BaseSchema

from datetime import datetime,timezone

from pydantic import Field

from uuid import UUID,uuid4

class BlacklistedTokenModel(BaseSchema):
    id:UUID = Field(default_factory=uuid4)
    jti: str
    user_id: str
    expires_at: datetime =Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )