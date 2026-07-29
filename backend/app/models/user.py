from datetime import datetime
from typing import Optional, List
from beanie import Document, Indexed
from pydantic import EmailStr, Field
from pymongo import ASCENDING


class User(Document):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    
    alert_threshold: float = 0.7
    default_layers: List[str] = Field(default_factory=lambda: ["earthquakes", "fires", "aqi", "flights", "ships"])
    units: str = "metric"
    offline_mode: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Settings:
        name = "users"
        indexes = [
            [("email", ASCENDING)],
            [("is_active", ASCENDING)],
        ]