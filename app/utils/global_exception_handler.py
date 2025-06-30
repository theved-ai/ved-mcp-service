import os

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config.logging_config import logger
from app.utils.application_constants import app_env_key


def _build_error_response(
        user_msg: str,
        status_code: int,
        debug_msg: str = None,
        code: str = None
):
    app_env = os.getenv(app_env_key)
    response = {
        "error": user_msg,
    }
    if code:
        response["code"] = code
    if app_env in ("local", "dev") and debug_msg:
        response["debug"] = debug_msg
    return JSONResponse(status_code=status_code, content=response)

async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        return await _handle_http_exception(request, exc)
    elif isinstance(exc, RequestValidationError):
        return await _handle_validation_exception(request, exc)
    else:
        return await _handle_unhandled_exception(request, exc)


async def _handle_http_exception(request: Request, exc: StarletteHTTPException):
    logger.warning(
        "HTTPException",
        exc_info=exc,
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method
        }
    )
    return _build_error_response(
        user_msg=exc.detail,
        debug_msg=repr(exc),
        status_code=exc.status_code,
        code="http_error"
    )


async def _handle_validation_exception(request: Request, exc: RequestValidationError):
    logger.warning(
        "RequestValidationError",
        exc_info=exc,
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors()
        }
    )
    return _build_error_response(
        user_msg="Validation Failed",
        debug_msg=str(exc.errors()),
        status_code=422,
        code="validation_error"
    )


async def _handle_unhandled_exception(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        extra={
            "path": request.url.path,
            "method": request.method,
        }
    )
    return _build_error_response(
        user_msg="Internal Server Error",
        debug_msg=repr(exc),
        status_code=500,
        code="internal_error"
    )
