from datetime import datetime
from typing import Optional, Dict, Any, List
from beanie import Document, Indexed
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, GEOSPHERE


class Event(Document):
    source: Indexed(str)
    domain: Indexed(str)
    event_type: Indexed(str)
    severity: Indexed(float)
    geometry: Dict[str, Any]
    properties: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Indexed(datetime)
    
    class Settings:
        name = "events"
        indexes = [
            [("timestamp", DESCENDING)],
            [("domain", ASCENDING), ("timestamp", DESCENDING)],
            [("severity", DESCENDING), ("timestamp", DESCENDING)],
            [("geometry", GEOSPHERE)],
            [("source", ASCENDING)],
            [("event_type", ASCENDING)],
            [("metadata.severity_tier", ASCENDING)],
        ]