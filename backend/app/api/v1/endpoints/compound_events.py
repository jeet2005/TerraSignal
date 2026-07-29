from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel

from app.models.compound_event import CompoundEvent
from app.models.event import Event
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_active_user


router = APIRouter()


class CompoundEventResponse(BaseModel):
    id: str
    detected_at: datetime
    expires_at: datetime
    centroid: dict
    radius_km: float
    domains: List[str]
    event_ids: List[str]
    severity: float
    severity_tier: str
    news_headlines: List[str]
    status: str
    
    class Config:
        from_attributes = True


class CompoundEventListResponse(BaseModel):
    events: List[CompoundEventResponse]
    total: int
    page: int
    page_size: int


class StatCardsResponse(BaseModel):
    active_high_severity_clusters: int
    total_events_last_hour: int
    most_active_domain: str


@router.get("", response_model=CompoundEventListResponse)
async def list_compound_events(
    status: str = "active",
    severity_min: float = 0.0,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
):
    query = {"status": status}
    if severity_min > 0:
        query["severity"] = {"$gte": severity_min}
    
    total = await CompoundEvent.find(query).count()
    events = await CompoundEvent.find(query).sort(-CompoundEvent.severity).skip((page - 1) * page_size).limit(page_size).to_list()
    
    return CompoundEventListResponse(
        events=[CompoundEventResponse(**e.model_dump(), id=str(e.id)) for e in events],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=StatCardsResponse)
async def get_compound_stats(
    current_user: User = Depends(get_current_active_user),
):
    active_count = await CompoundEvent.find({"status": "active", "severity": {"$gte": 0.7}}).count()
    
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    total_events = await Event.find({"timestamp": {"$gte": hour_ago}}).count()
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": hour_ago}}},
        {"$group": {"_id": "$domain", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    domain_result = await Event.aggregate(pipeline).to_list()
    most_active = domain_result[0]["_id"] if domain_result else "none"
    
    return StatCardsResponse(
        active_high_severity_clusters=active_count,
        total_events_last_hour=total_events,
        most_active_domain=most_active,
    )


@router.get("/{event_id}", response_model=CompoundEventResponse)
async def get_compound_event(
    event_id: str,
    current_user: User = Depends(get_current_active_user),
):
    event = await CompoundEvent.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Compound event not found")
    return CompoundEventResponse(**event.model_dump(), id=str(event.id))