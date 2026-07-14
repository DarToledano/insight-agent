"""Aggregate API routers."""

from fastapi import APIRouter

from app.api import ask, generate_sql, health, metadata, schema

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(schema.router)
api_router.include_router(metadata.router)
api_router.include_router(ask.router)
api_router.include_router(generate_sql.router)
