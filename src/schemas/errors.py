"""
Pydantic schemas for Errors.
"""

from pydantic import BaseModel, Field
from src.utils.constants import (
    MESSAGE_RESOURCE_NOT_FOUND,
    MESSAGE_RESOURCE_ALREADY_EXISTS,
)


class ResourceNotFoundErrorResponse(BaseModel):
    """Error for 404 not found resource."""

    detail: str = Field(
        json_schema_extra={
            "example": MESSAGE_RESOURCE_NOT_FOUND.format(
                resource="<resource>", key="<key>", value="<value>"
            )
        }
    )


class ResourceAlreadyExistsErrorResponse(BaseModel):
    """Error for 409 conflicts."""

    detail: str = Field(
        json_schema_extra={
            "example": MESSAGE_RESOURCE_ALREADY_EXISTS.format(
                resource="<resource>", key="<key>", value="<value>"
            )
        }
    )
    resource: str = Field(json_schema_extra={"example": "<resource>"})
    key: str = Field(json_schema_extra={"example": "<name>"})
    value: str = Field(json_schema_extra={"example": "<value>"})


class InternalServerErrorResponse(BaseModel):
    """Error for 5xx server errors."""

    detail: str = Field(json_schema_extra={"example": "Internal Server Error"})
