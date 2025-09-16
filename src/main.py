"""
Main entry point for the FastAPI application.

Initializes the FastAPI app, registers all routers, and configures
global exception handlers. If run directly, starts a Uvicorn server.
"""

import traceback
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


from src.api import root, utils, contacts
from src.config.app_config import config
from src.utils.constants import MESSAGE_ERROR_INTERNAL_SERVER_ERROR
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(
    _app: FastAPI,
) -> AsyncIterator[None]:  # pylint: disable=unused-argument
    """
    Application lifespan context manager.

    Runs once on startup and shutdown. Place resource initialization
    or cleanup tasks here (e.g., database connections).
    """
    logger.info("Application startup initiated")
    yield
    logger.info("Application shutdown complete")


app = FastAPI(
    lifespan=lifespan,
    title="Contacts Manager API",
    description="REST API for storing and managing personal contacts.",
)

app.include_router(root.router)
app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic/body/query validation failures (HTTP 422).

    Logs the validation errors and returns the standard FastAPI error format.
    """
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url,
        exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle all Starlette and FastAPI HTTPExceptions and unify response."""
    logger.info(
        "HTTP %s: %s %s%s",
        exc.status_code,
        request.method,
        request.url.path,
        f"?{request.url.query}" if request.url.query else "",
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def handle_global_exception(
    request: Request, exc: Exception  # pylint: disable=unused-argument
) -> JSONResponse:
    """Catch all unhandled exceptions."""
    logger.exception("Unhandled exception: %s", exc)
    if config.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": f"Unhandled exceptions caused {MESSAGE_ERROR_INTERNAL_SERVER_ERROR}",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": MESSAGE_ERROR_INTERNAL_SERVER_ERROR},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=config.WEB_PORT, reload=config.DEBUG
    )
