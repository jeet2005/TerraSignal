from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document, Indexed
from pymongo import ASCENDING, DESCENDING


class PushSubscription(Document):
    user_id: Indexed(str)
    endpoint: str
    keys: Dict[str, str]
    user_agent: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    
    class Settings:
        name = "push_subscriptions"
        indexes = [
            [("user_id", ASCENDING)],
            [("active", ASCENDING)],
            [("endpoint", ASCENDING)],
        ]