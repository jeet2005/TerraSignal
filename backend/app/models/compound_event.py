from datetime import datetime
from typing: List, Optional, Dict, Any
from beanie import Document, Indexed
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, GEOSPHERE


class CompoundEvent(Document):
    start_time: Indexed(datetime)
    end_time: Indexed(datetime)
    detected_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    expires_at: Indexed(datetime)
    centroid: Dict[str, Any]
    radius_km: float
    domains: List[str]
    event_ids: List[str]
    event_count: int
    time_span_hours: float
    severity: Indexed(float)
    severity_tier: str
    amplification_factor: float = 1.0
    news_headlines: List[str] = Field(default_factory=list)
    status: str = "active"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "compound_events"
        indexes = [
            [("start_time", DESCENDING)],
            [("detected_at", DESCENDING)],
            [("severity", DESCENDING), ("detected_at", DESCENDING)],
            [("status", ASCENDING)],
            [("centroid", GEOSPHERE)],
            [("domains", ASCENDING)],
            [("expires_at", ASCENDING)],
        ]