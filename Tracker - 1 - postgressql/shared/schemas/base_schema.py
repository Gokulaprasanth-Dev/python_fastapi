from pydantic import BaseModel, ConfigDict

from uuid import UUID

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        json_encoders={
            UUID: str
        }
    )
