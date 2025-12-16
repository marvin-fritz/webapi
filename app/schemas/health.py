"""Health check schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str
    app_name: str
    version: str

