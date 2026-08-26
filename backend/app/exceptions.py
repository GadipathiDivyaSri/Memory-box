"""
MemoryBox Standardized Exception Handlers
Standardizes error payloads across all endpoints to ensure clean JSON responses.
"""

import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger("memorybox.exceptions")


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Standardizes HTTP error responses:
    Returns {"status": "error", "detail": ..., "status_code": ...}
    """
    logger.warning(f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail,
            "path": request.url.path,
            "status_code": exc.status_code
        },
        headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Standardizes Pydantic input validation error responses.
    """
    logger.warning(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    # Format readable details
    details = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        details.append(f"{field}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "detail": "; ".join(details) if details else str(exc.errors()),
            "errors": exc.errors(),
            "path": request.url.path,
            "status_code": 422
        }
    )
