from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from beanie.operators import And, Or
from pymongo import DESCENDING

from app.models.event import Event
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_active_user


router = APIRouter()


class EventResponse(BaseModel):
    id: str
    source: str
    domain: str
    event_type: str
    severity: float
    geometry: dict
    properties: dict
    metadata: dict
    timestamp: datetime
    
    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=EventListResponse)
async def list_events(
    domain: Optional[str] = None,
    event_type: Optional[str] = None,
    severity_min: float = 0.0,
    severity_max: float = 1.0,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: Optional[float] = None,
    hours: int = 24,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
):
    query = {}
    
    if domain:
        query["domain"] = domain
    if event_type:
        query["event_type"] = event_type
    if severity_min > 0 or severity_max < 1.0:
        query["severity"] = {"$gte": severity_min, "$lte": severity_max}
    
    since = datetime.utcnow() - timedelta(hours=hours)
    query["timestamp"] = {"$gte": since}
    
    if lat is not None and lon is not None and radius_km:
        query["geometry"] = {
            "$nearSphere": {
                "$geometry": {"type": "Point", "coordinates": [lon, lat]},
                "$maxDistance": radius_km * 1000,
            }
        }
    
    total = await Event.find(query).count()
    events = await Event.find(query).sort(-Event.timestamp).skip((page - 1) * page_size).limit(page_size).to_list()
    
    return EventListResponse(
        events=[EventResponse(**e.model_dump(), id=str(e.id)) for e in events],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/latest", response_model=List[EventResponse])
async def get_latest_events(
    limit: int = Query(100, ge=1, le=500),
    domain: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    query = {}
    if domain:
        query["domain"] = domain
    
    events = await Event.find(query).sort(-Event.timestamp).limit(limit).to_list()
    return [EventResponse(**e.model_dump(), id=str(e.id)) for e in events]


@router.get("/domains", response_model=List[str])
async def get_domains(current_user: User = Depends(get_current_active_user)):
    domains = await Event.distinct("domain")
    return sorted(domains)


@router.get("/types", response_model=List[str])
async def get_event_types(
    domain: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    query = {}
    if domain:
        query["domain"] = domain
    types = await Event.distinct("event_type", query)
    return sorted(types)


@router.get("/stats", response_model=dict)
async def get_event_stats(
    hours: int = 24,
    current_user: User = Depends(get_current_active_user),
):
    since = datetime.utcnow() - timedelta(hours=hours)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": "$domain",
            "count": {"$sum": 1},
            "avg_severity": {"$avg": "$severity"},
            "max_severity": {"$max": "$severity"},
        }},
        {"$sort": {"count": -1}}
    ]
    
    results = await Event.aggregate(pipeline).to_list()
    
    return {
        "period_hours": hours,
        "domains": [
            {
                "domain": r["_id"],
                "count": r["count"],
                "avg_severity": round(r["avg_severity"], 3),
                "max_severity": round(r["max_severity"], 3),
            }
            for r in results
        ],
        "total": sum(r["count"] for r in results),
    }


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    current_user: User = Depends(get_current_active_user),
):
    event = await Event.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse(**event.model_dump(), id=str(event.id))