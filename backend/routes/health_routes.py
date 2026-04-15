"""Health check routes."""

from fastapi import APIRouter
from backend.db.mongodb import get_database
from backend.utils.response import APIResponse
import os

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health_check():
    return APIResponse.success(data={"status": "healthy"}, message="API is running")


@router.get("/db")
async def db_health():
    try:
        db = get_database()
        await db.command("ping")
        return APIResponse.success(data={"mongodb": "connected"})
    except Exception as e:
        return APIResponse.error(message=f"DB connection failed: {e}", status_code=500)


@router.get("/ml")
async def ml_health():
    from backend.config import settings
    model_exists = os.path.exists(settings.MODEL_PATH)
    return APIResponse.success(data={"model_loaded": model_exists})