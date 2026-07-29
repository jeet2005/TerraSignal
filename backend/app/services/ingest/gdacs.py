import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


GDACS_BASE_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"


def calculate_severity(domain: str, **kwargs) -> float:
    if domain == "disaster":
        alert_level = kwargs.get("alert_level", "Green")
        if alert_level == "Red":
            return 1.0
        elif alert_level == "Orange":
            return 0.7
        elif alert_level == "Yellow":
            return 0.4
        else:
            return 0.1
    return 0.1


async def fetch_gdacs_events() -> List[Dict]:
    params = {
        "format": "json",
        "alertlevel": "all",
        "eventtype": "all",
        "fromdate": "",
        "todate": "",
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(GDACS_BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("features", [])
        except Exception as e:
            logger.error("gdacs_fetch_failed", error=str(e))
            return []


def normalize_gdacs_event(feature: Dict) -> Optional[Event]:
    try:
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        
        alert_level = props.get("alertlevel", "Green")
        severity = calculate_severity("disaster", alert_level=alert_level)
        
        coords = geom.get("coordinates", [0, 0])
        
        return Event(
            source="gdacs",
            domain="disaster",
            event_type=props.get("eventtype", "").lower(),
            severity=severity,
            geometry={"type": "Point", "coordinates": coords},
            properties={
                "event_id": props.get("eventid"),
                "event_name": props.get("eventname"),
                "event_type": props.get("eventtype"),
                "alert_level": alert_level,
                "country": props.get("country"),
                "area": props.get("area"),
                "latitude": props.get("latitude"),
                "longitude": props.get("longitude"),
                "depth": props.get("depth"),
                "magnitude": props.get("magnitude"),
                "magnitude_unit": props.get("magnitudeunit"),
                "population": props.get("population"),
                "vulnerability": props.get("vulnerability"),
                "coping_capacity": props.get("copingcapacity"),
                "description": props.get("description"),
                "url": props.get("url"),
                "from_date": props.get("fromdate"),
                "to_date": props.get("todate"),
            },
            metadata={
                "severity_tier": "critical" if severity >= 0.8 else "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
            },
            timestamp=props.get("fromdate", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("gdacs_normalize_failed", error=str(e))
        return None