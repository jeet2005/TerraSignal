import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


ACLED_BASE_URL = "https://api.acleddata.com/acled/read"


async def fetch_acled_events(
    api_key: str,
    email: str,
    limit: int = 100,
    start_date: str = None,
    end_date: str = None,
    country: str = None,
    event_type: str = None,
) -> List[Dict]:
    params = {
        "key": api_key,
        "email": email,
        "limit": limit,
        "format": "json",
    }
    
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if country:
        params["country"] = country
    if event_type:
        params["event_type"] = event_type
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(ACLED_BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])
        except Exception as e:
            logger.error("acled_fetch_failed", error=str(e))
            return []


def normalize_acled_event(event: Dict) -> Optional[Event]:
    try:
        lat = event.get("latitude")
        lon = event.get("longitude")
        
        if lat is None or lon is None:
            return None
        
        fatalities = event.get("fatalities", 0)
        if fatalities >= 100:
            severity = 1.0
        elif fatalities >= 10:
            severity = 0.8
        elif fatalities >= 1:
            severity = 0.6
        else:
            severity = 0.3
        
        return Event(
            source="acled",
            domain="conflict",
            event_type=event.get("event_type", "").lower().replace(" ", "_"),
            severity=severity,
            geometry={"type": "Point", "coordinates": [float(lon), float(lat)]},
            properties={
                "data_id": event.get("data_id"),
                "event_id_cnty": event.get("event_id_cnty"),
                "event_date": event.get("event_date"),
                "year": event.get("year"),
                "time_precision": event.get("time_precision"),
                "disorder_type": event.get("disorder_type"),
                "event_type": event.get("event_type"),
                "sub_event_type": event.get("sub_event_type"),
                "actor1": event.get("actor1"),
                "actor2": event.get("actor2"),
                "interaction": event.get("interaction"),
                "country": event.get("country"),
                "admin1": event.get("admin1"),
                "admin2": event.get("admin2"),
                "location": event.get("location"),
                "latitude": lat,
                "longitude": lon,
                "geo_precision": event.get("geo_precision"),
                "source": event.get("source"),
                "notes": event.get("notes"),
                "fatalities": fatalities,
                "tags": event.get("tags"),
            },
            metadata={
                "severity_tier": "critical" if severity >= 0.8 else "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low",
            },
            timestamp=event.get("event_date", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("acled_normalize_failed", error=str(e))
        return None