from uuid import UUID

from shared.schemas.base_schema import BaseSchema


class AvatarUploadResponse(BaseSchema):
    user_id: UUID
    profile_image_url: str