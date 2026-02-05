"""
Custom exception classes and handlers
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


class BaseCustomException(Exception):
    """Base custom exception"""

    def __init__(self, message: str, status_code: int = HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(BaseCustomException):
    """Resource not found exception"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, HTTP_404_NOT_FOUND)


class BadRequestException(BaseCustomException):
    """Bad request exception"""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message, HTTP_400_BAD_REQUEST)


class ValidationException(BaseCustomException):
    """Validation exception"""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, HTTP_400_BAD_REQUEST)


async def base_custom_exception_handler(
    request: Request, exc: BaseCustomException
) -> JSONResponse:
    """Handle custom exceptions"""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(exc)})


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions"""
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
