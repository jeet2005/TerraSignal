import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.event import Event
from app.core.logging import logger


USGS_BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def calculate_severity(domain: str, value: float) -> float:
    if domain == "seismic":
        if value >= 7.0:
            return 1.0
        elif value >= 6.0:
            return 0.8
        elif value >= 5.0:
            return 0.6
        elif value >= 4.0:
            return 0.4
        elif value >= 3.0:
            return 0.3
        elif value >= 2.0:
            return 0.2
        else:
            return 0.1
    return 0.1


async def fetch_usgs_events() -> List[Dict]:
    params = {
        "format": "geojson",
        "starttime": datetime.utcnow().replace(hour=0, minute=0, second=0).isoformat() + "Z",
        "minmagnitude": 1.0,
        "orderby": "time",
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(USGS_BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("features", [])
        except Exception as e:
            logger.error("usgs_fetch_failed", error=str(e))
            return []


def normalize_usgs_event(event: Dict) -> Optional[Event]:
    try:
        props = event.get("properties", {})
        geom = event.get("geometry", {})
        coords = geom.get("coordinates", [0, 0, 0])
        
        magnitude = props.get("mag", 0)
        severity = calculate_severity("seismic", magnitude)
        
        return Event(
            source="usgs",
            domain="seismic",
            event_type="earthquake",
            severity=severity,
            geometry={"type": "Point", "coordinates": [coords[0], coords[1]]},
            properties={
                "magnitude": magnitude,
                "depth": coords[2] if len(coords) > 2 else 0,
                "place": props.get("place"),
                "url": props.get("url"),
                "felt": props.get("felt"),
                "cdi": props.get("cdi"),
                "mmi": props.get("mmi"),
                "alert": props.get("alert"),
                "status": props.get("status"),
                "tsunami": props.get("tsunami"),
                "sig": props.get("sig"),
                "net": props.get("net"),
                "code": props.get("code"),
                "ids": props.get("ids"),
                "sources": props.get("sources"),
                "types": props.get("types"),
                "nst": props.get("nst"),
                "dmin": props.get("dmin"),
                "rms": props.get("rms"),
                "gap": props.get("gap"),
                "magType": props.get("magType"),
                "type": props.get("type"),
                "title": props.get("title"),
            },
            metadata={
                "severity_tier": "critical" if severity >= 0.8 else "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
                "source_updated": datetime.fromtimestamp(props.get("updated", 0) / 1000).isoformat() if props.get("updated") else None,
            },
            timestamp=datetime.fromtimestamp(props.get("time", 0) / 1000).isoformat() if props.get("time") else datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("usgs_normalize_failed", error=str(e))
        return None