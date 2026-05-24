"""
Shared error response schema.

Used by exception handlers to produce a consistent JSON error envelope
across all modules.

Shape:
    {
        "error": {
            "code": "USER_NOT_FOUND",
            "message": "User not found",
            "details": {"user_id": "abc123"}
        }
    }
"""

from typing import Any

from shared.schemas.base_schema import BaseSchema


class ErrorDetail(BaseSchema):
    code: str
    message: str
    details: dict[str, Any] = {}


class ErrorResponse(BaseSchema):
    error: ErrorDetail
