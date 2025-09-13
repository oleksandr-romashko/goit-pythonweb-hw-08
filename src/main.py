"""
Main entry point for the FastAPI application.

This module initializes the FastAPI app, registers all routers, and
starts the Uvicorn development server if run as a script.
"""

import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


from src.api import root, utils
from src.config.app_config import config
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(_app: FastAPI):  # pylint: disable=unused-argument
    """Lifespan context manager for application startup and shutdown."""
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    lifespan=lifespan,
    title="Contacts Manager API",
    description="API to store and manage your contacts.",
)

app.include_router(root.router)
app.include_router(utils.router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Catches Pydantic/body/query validation failures (default status 422)."""
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
def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle all Starlet and FastAPI HTTPExceptions (incl. 404)."""
    logger.info(
        "HTTP %s: %s %s%s",
        exc.status_code,
        request.method,
        request.url.path,
        f"?{request.url.query}" if request.url.query else "",
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def handle_global_exception(
    request: Request, exc: Exception  # pylint: disable=unused-argument
) -> JSONResponse:
    """
    Catch all unhandled exceptions.

    Last-resort catch-all to avoid crashing and to log tracebacks.
    Logs the full traceback. Returns a safe 500 JSON response in production,
    and includes the exception message and traceback in debug mode.
    """
    logger.exception("Unhandled exception: %s", exc)
    if config.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal Server Error",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=config.WEB_PORT, reload=config.DEBUG
    )
