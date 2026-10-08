from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

_HTTP_CODES = {404: "not_found", 405: "method_not_allowed"}


class AppError(Exception):
    """A failure the client should see, with a stable machine-readable code."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class ErrorBody(BaseModel):
    code: str = Field(description="Stable machine-readable code.", examples=["course_unavailable"])
    message: str = Field(description="Human-readable explanation.", examples=["French is coming soon."])
    details: Any | None = Field(
        default=None, description="Only for validation_error: one entry per invalid field."
    )


class ErrorOut(BaseModel):
    """The body of every error response."""

    error: ErrorBody


def error_response(description: str) -> dict[str, Any]:
    """An OpenAPI `responses` entry for an error status, so /docs shows the real error shape."""
    return {"model": ErrorOut, "description": description}


def _error(status_code: int, code: str, message: str, details: Any = None) -> JSONResponse:
    body = ErrorOut(error=ErrorBody(code=code, message=message, details=details))
    return JSONResponse(status_code=status_code, content=body.model_dump(exclude_none=True))


def register_error_handlers(app: FastAPI) -> None:
    """Every error leaves the API as {"error": {"code", "message", "details"?}}."""

    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        return _error(exc.status_code, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return _error(422, "validation_error", "The request is invalid.", jsonable_encoder(exc.errors()))

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _error(exc.status_code, _HTTP_CODES.get(exc.status_code, "http_error"), str(exc.detail))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_request: Request, _exc: Exception) -> JSONResponse:
        # Starlette re-raises the exception after sending this response, so the server still logs it.
        return _error(500, "internal_error", "Something went wrong on our side.")
