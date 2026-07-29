from fastapi import APIRouter

from app.api.v1.endpoints import auth, events, compound_events, push, settings, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(compound_events.router, prefix="/compound", tags=["compound-events"])
api_router.include_router(push.router, prefix="/push", tags=["push-notifications"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])