"""
Helper module for raising errors.
"""

from typing import Any, NoReturn

from fastapi import HTTPException, status
from src.utils.constants import (
    MESSAGE_RESOURCE_NOT_FOUND,
    MESSAGE_RESOURCE_ALREADY_EXISTS,
)


def _raise_http_error(
    status_code: int, message_template: str, resource: str, key: str, value: Any
) -> NoReturn:
    """Common error template"""
    error_payload = {
        "detail": message_template.format(resource=resource, key=key, value=value),
        "resource": resource,
        "key": key,
        "value": value,
    }
    raise HTTPException(status_code=status_code, detail=error_payload)


def raise_http_404_not_found(resource: str, key: str, value: Any) -> NoReturn:
    """Raise a 404 Not Found error with consistent payload."""
    _raise_http_error(
        status.HTTP_404_NOT_FOUND, MESSAGE_RESOURCE_NOT_FOUND, resource, key, value
    )


def raise_http_409_conflict(resource: str, key: str, value: Any) -> NoReturn:
    """Raise a 409 Conflict error with consistent payload."""
    _raise_http_error(
        status.HTTP_409_CONFLICT, MESSAGE_RESOURCE_ALREADY_EXISTS, resource, key, value
    )


def raise_http_500(detail: str = "Internal Server Error") -> None:
    """Raise a 500 Internal Server Error with consistent payload."""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"detail": detail},
    )
