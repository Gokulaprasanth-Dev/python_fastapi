from datetime import datetime, timezone

from pydantic import Field

from uuid import UUID, uuid4

from shared.schemas.base_schema import BaseSchema


class CompanyModel(BaseSchema):

    id: UUID = Field(default_factory=uuid4)

    name: str          # FIX #8: was str | None — always provided at registration
    country: str       # FIX #8: was str | None
    industry: str      # FIX #8: was str | None

    is_active: bool = True
    is_verified: bool = False

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )