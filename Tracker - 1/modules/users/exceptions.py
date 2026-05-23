from core.exceptions.base import ConflictError, NotFoundError


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