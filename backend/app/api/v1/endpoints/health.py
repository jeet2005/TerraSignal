from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.models.user import User
from app.api.v1.endpoints.auth import get_current_active_user


router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str


@router.get("", response_model=HealthResponse)
async def health_check():
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        service="terrasignal-api",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/ready")
async def readiness_check(current_user: User = Depends(get_current_active_user)):
    from app.core.database import get_database
    db = get_database()
    try:
        await db.command("ping")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not ready", "database": "disconnected", "error": str(e)}