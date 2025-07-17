from fastapi import HTTPException


class ExternalAPIError(HTTPException):
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(status_code=status_code, detail=message)


class ValidationError(HTTPException):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=message)


class NotFoundError(HTTPException):
    def __init__(self, message: str = "Resource not found", status_code: int = 404):
        super().__init__(status_code=status_code, detail=message)