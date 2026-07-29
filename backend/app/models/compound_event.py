from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Document, Indexed
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, GEOSPHERE


class CompoundEvent(Document):
    detected_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    expires_at: Indexed(datetime)
    centroid: Dict[str, Any]
    radius_km: float
    domains: List[str]
    event_ids: List[str]
    severity: Indexed(float)
    severity_tier: str
    news_headlines: List[str] = Field(default_factory=list)
    status: str = "active"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "compound_events"
        indexes = [
            [("detected_at", DESCENDING)],
            [("severity", DESCENDING), ("detected_at", DESCENDING)],
            [("status", ASCENDING)],
            [("centroid", GEOSPHERE)],
            [("domains", ASCENDING)],
            [("expires_at", ASCENDING)],
        ]