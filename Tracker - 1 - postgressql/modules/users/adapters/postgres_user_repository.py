from datetime import datetime, timezone

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.tables.user_table import UserTable
from modules.users.model import UserModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _row_to_dict(row: UserTable | None) -> dict | None:
    if row is None:
        return None
    return {
        "id": str(row.id),
        "company_id": str(row.company_id),
        "email": row.email,
        "hashed_password": row.hashed_password,
        "full_name": row.full_name,
        "phone": row.phone,
        "gender": row.gender,
        "desc": row.desc,
        "profile_image_url": row.profile_image_url,
        "role": row.role,
        "is_active": row.is_active,
        "is_verified": row.is_verified,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
        "last_login": row.last_login,
    }


class PostgresUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def email_exist(self, email: str) -> bool:
        result = await self.session.execute(
            select(UserTable.id).where(UserTable.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def create_user(self, user: UserModel, session: AsyncSession | None = None) -> str:
        db = session or self.session
        row = UserTable(
            id=user.id,
            company_id=user.company_id,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            phone=user.phone,
            gender=user.gender,
            desc=user.desc,
            profile_image_url=user.profile_image_url,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
        db.add(row)
        await db.flush()
        return str(user.id)

    async def get_user_by_email(self, email: str) -> dict | None:
        result = await self.session.execute(
            select(UserTable).where(UserTable.email == email)
        )
        return _row_to_dict(result.scalar_one_or_none())

    async def get_user_by_id(self, user_id: str) -> dict | None:
        import uuid
        try:
            uid = uuid.UUID(user_id)
        except ValueError:
            return None
        result = await self.session.execute(
            select(UserTable).where(UserTable.id == uid)
        )
        return _row_to_dict(result.scalar_one_or_none())

    async def update_user(self, user_id: str, updates: dict, session: AsyncSession | None = None) -> bool:
        import uuid
        db = session or self.session
        updates["updated_at"] = _now()
        result = await db.execute(
            update(UserTable)
            .where(UserTable.id == uuid.UUID(user_id))
            .values(**updates)
        )
        return result.rowcount > 0

    async def update_profile_image(self, user_id: str, url: str, session: AsyncSession | None = None) -> bool:
        import uuid
        db = session or self.session
        result = await db.execute(
            update(UserTable)
            .where(UserTable.id == uuid.UUID(user_id))
            .values(profile_image_url=url, updated_at=_now())
        )
        return result.rowcount > 0

    async def soft_delete_user(self, user_id: str, session: AsyncSession | None = None) -> bool:
        import uuid
        db = session or self.session
        result = await db.execute(
            update(UserTable)
            .where(UserTable.id == uuid.UUID(user_id))
            .values(is_active=False, updated_at=_now())
        )
        return result.rowcount > 0

    async def hard_delete_user(self, user_id: str, session: AsyncSession | None = None) -> bool:
        import uuid
        db = session or self.session
        result = await db.execute(
            delete(UserTable).where(UserTable.id == uuid.UUID(user_id))
        )
        return result.rowcount > 0
