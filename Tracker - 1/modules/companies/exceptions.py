from core.exceptions.base import NotFoundError, ConflictError


class CompanyNotFoundError(NotFoundError):
    error_code = "COMPANY_NOT_FOUND"

    def __init__(self, company_id: str) -> None:
        super().__init__(
            message="Company not found",
            details={"company_id": company_id},
        )


class CompanyNameAlreadyExistsError(ConflictError):
    error_code = "COMPANY_NAME_EXISTS"

    def __init__(self, name: str) -> None:
        super().__init__(
            message="A company with this name already exists",
            details={"name": name},
        )
