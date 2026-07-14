"""Response schemas for health endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class DbHealthResponse(BaseModel):
    status: str
    database: str
    message: str
