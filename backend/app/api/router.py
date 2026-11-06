from fastapi import APIRouter

from app.api.v1.endpoints import characters, health, reference_data

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(characters.router)
api_router.include_router(reference_data.router)
