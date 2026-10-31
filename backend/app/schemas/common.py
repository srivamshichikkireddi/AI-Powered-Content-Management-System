from typing import Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Standard error envelope required by SAD §4.3 and Non-Negotiable Rules:
    { code, message, correlation_id }
    """
    code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Human-readable safe explanation")
    correlation_id: str = Field(..., description="Tracing correlation ID")


class HealthResponse(BaseModel):
    """
    Service health check response schema (TC-OPS-01).
    """
    status: str = Field("healthy", description="Overall service status")
    database: str = Field("connected", description="Database connection health")
    redis: str = Field("connected", description="Redis connection health")
    timestamp: str = Field(..., description="ISO 8601 server timestamp")
    version: str = Field("1.0.0", description="API version")
    environment: str = Field(..., description="Deployment environment")
