from core.exceptions.base import ConflictError, NotFoundError, ValidationError


class EmailAlreadyExistsError(ConflictError):
    error_code = "EMAIL_ALREADY_EXISTS"

    def __init__(self, email: str) -> None:
        super().__init__(
            message="Email already registered",
            details={"email": email},
        )


class UserNotFoundError(NotFoundError):
    error_code = "USER_NOT_FOUND"

    def __init__(self, user_id: str) -> None:
        super().__init__(
            message="User not found",
            details={"user_id": user_id},
        )


class UnsupportedFileTypeError(ValidationError):
    error_code = "UNSUPPORTED_FILE_TYPE"

    def __init__(self, content_type: str, allowed: list[str]) -> None:
        super().__init__(
            message="Unsupported file type",
            details={"content_type": content_type, "allowed": allowed},
        )


class FileTooLargeError(ValidationError):
    error_code = "FILE_TOO_LARGE"

    def __init__(self, max_bytes: int) -> None:
        super().__init__(
            message="Uploaded file exceeds the size limit",
            details={"max_bytes": max_bytes},
        )
