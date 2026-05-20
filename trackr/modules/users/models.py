from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class UserDocument:
    full_name: str
    email: str
    hashed_password: str
    phone: str
    company_id: UUID
    role: str = "admin"
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
