"""Base schemas with common configurations."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,  # Allow creating from ORM models
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for schemas with timestamps."""

    created_at: datetime
    updated_at: datetime | None = None


class PaginatedResponse(BaseModel):
    """Generic paginated response schema."""

    items: list
    total: int
    page: int
    page_size: int
    pages: int

