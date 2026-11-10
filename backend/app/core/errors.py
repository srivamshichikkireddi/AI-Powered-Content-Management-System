import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.logging import get_correlation_id

logger = logging.getLogger(__name__)


class AICMSException(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AICMSException)
    async def aicms_exception_handler(request: Request, exc: AICMSException) -> JSONResponse:
        cid = get_correlation_id()
        logger.warning(f"Business error [{exc.code}]: {exc.message} (cid: {cid})")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "correlation_id": cid,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        cid = get_correlation_id()
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            423: "LOCKED",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_SERVER_ERROR",
        }
        code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
        message = str(exc.detail) if exc.detail else "An error occurred"

        logger.info(f"HTTP exception [{code}]: {message} (cid: {cid})")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": code,
                "message": message,
                "correlation_id": cid,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        cid = get_correlation_id()
        errors = exc.errors()
        first_msg = errors[0].get("msg", "Validation error") if errors else "Validation failed"
        field = ".".join(str(loc) for loc in errors[0].get("loc", [])) if errors else ""
        detail_msg = f"{field}: {first_msg}" if field else first_msg

        logger.warning(f"Validation error: {detail_msg} (cid: {cid})")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": "VALIDATION_ERROR",
                "message": detail_msg,
                "correlation_id": cid,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        cid = get_correlation_id()
        logger.error(f"Unhandled exception: {str(exc)} (cid: {cid})", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal system error occurred. Please contact the administrator.",
                "correlation_id": cid,
            },
        )
