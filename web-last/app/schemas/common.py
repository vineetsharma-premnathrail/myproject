"""
Common Schemas Module
--------------------
Purpose:
    Defines shared Pydantic models used across multiple API endpoints.
    Provides standardized response formats for health checks, errors,
    and success responses throughout the application.
Layer:
    Backend / Schemas / Common
"""

from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    """
    Standardized health check response model.

    Used by health monitoring endpoints to report system status.
    Provides consistent format for load balancers and monitoring systems.

    Attributes:
        status: System health status ("healthy" or "unhealthy")
        version: Application version string
        database: Database connection status or error message
    """
    status: str
    version: str
    database: str


class ErrorResponse(BaseModel):
    """
    Standardized error response model for API failures.

    Provides consistent error format across all API endpoints.
    Helps clients handle errors uniformly.

    Attributes:
        error: Error type or code (e.g., "validation_error", "not_found")
        message: Human-readable error message
        details: Optional additional error details or context
    """
    error: str
    message: str
    details: Optional[dict] = None


class SuccessResponse(BaseModel):
    """
    Standardized success response model for API operations.

    Provides consistent success format across all API endpoints.
    Includes optional data payload for successful operations.

    Attributes:
        message: Success message describing the operation
        data: Optional data payload (varies by endpoint)
    """
    message: str
    data: Optional[dict] = None