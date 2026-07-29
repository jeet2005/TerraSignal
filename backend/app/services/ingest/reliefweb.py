import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


RELIEFWEB_BASE_URL = "https://api.reliefweb.int/v1"


async def fetch_reliefweb_disasters(
    limit: int = 100,
    offset: int = 0,
    fields: List[str] = None
) -> List[Dict]:
    url = f"{RELIEFWEB_BASE_URL}/disasters"
    params = {
        "limit": limit,
        "offset": offset,
        "appname": "terrasignal",
        "preset": "latest",
        "profile": "full",
    }
    
    if fields:
        params["fields[disaster]"] = ",".join(fields)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])
        except Exception as e:
            logger.error("reliefweb_disasters_fetch_failed", error=str(e))
            return []


async def fetch_reliefweb_reports(
    limit: int = 100,
    disaster_id: str = None
) -> List[Dict]:
    url = f"{RELIEFWEB_BASE_URL}/reports"
    params = {
        "limit": limit,
        "appname": "terrasignal",
        "preset": "latest",
        "profile": "full",
    }
    
    if disaster_id:
        params["filter[field]"] = "disaster.id"
        params["filter[value]"] = disaster_id
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])
        except Exception as e:
            logger.error("reliefweb_reports_fetch_failed", error=str(e))
            return []


def normalize_reliefweb_disaster(disaster: Dict) -> Optional[Event]:
    try:
        fields = disaster.get("fields", {})
        geom = disaster.get("geometry", {})
        coords = geom.get("coordinates", [0, 0])
        
        alert_level = fields.get("alert_level", "").lower()
        severity_map = {"high": 0.8, "medium": 0.5, "low": 0.2}
        severity = severity_map.get(alert_level, 0.3)
        
        return Event(
            source="reliefweb",
            domain="humanitarian",
            event_type="disaster",
            severity=severity,
            geometry={"type": "Point", "coordinates": coords},
            properties={
                "id": disaster.get("id"),
                "name": fields.get("name"),
                "type": fields.get("type", {}).get("name"),
                "status": fields.get("status"),
                "alert_level": alert_level,
                "primary_country": fields.get("primary_country", {}).get("name"),
                "countries": [c.get("name") for c in fields.get("countries", [])],
                "date_created": fields.get("date", {}).get("created"),
                "date_changed": fields.get("date", {}).get("changed"),
                "description": fields.get("description"),
                "url": fields.get("url"),
                "glide": fields.get("glide"),
            },
            metadata={
                "severity_tier": "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low",
            },
            timestamp=fields.get("date", {}).get("created", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("reliefweb_disaster_normalize_failed", error=str(e))
        return None


def normalize_reliefweb_report(report: Dict) -> Optional[Event]:
    try:
        fields = report.get("fields", {})
        geom = report.get("geometry", {})
        coords = geom.get("coordinates", [0, 0])
        
        return Event(
            source="reliefweb",
            domain="humanitarian",
            event_type="report",
            severity=0.2,
            geometry={"type": "Point", "coordinates": coords},
            properties={
                "id": report.get("id"),
                "title": fields.get("title"),
                "body": fields.get("body"),
                "type": fields.get("type", {}).get("name"),
                "source": fields.get("source", {}).get("name"),
                "language": fields.get("language", {}).get("name"),
                "date_created": fields.get("date", {}).get("created"),
                "url": fields.get("url"),
                "disasters": [d.get("name") for d in fields.get("disasters", [])],
                "countries": [c.get("name") for c in fields.get("countries", [])],
            },
            metadata={"severity_tier": "low"},
            timestamp=fields.get("date", {}).get("created", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("reliefweb_report_normalize_failed", error=str(e))
        return None