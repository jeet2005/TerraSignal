import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


GDELT_GEO_BASE_URL = "https://api.gdeltproject.org/api/v2/geo/geo"


async def fetch_gdelt_geo(
    date: str = None,
    country: str = None,
    theme: str = None,
    max_records: int = 250
) -> List[Dict]:
    if date is None:
        date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y%m%d")
    
    params = {
        "format": "json",
        "maxrecords": max_records,
        "date": date,
    }
    
    if country:
        params["country"] = country
    if theme:
        params["theme"] = theme
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.get(GDELT_GEO_BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("features", [])
        except Exception as e:
            logger.error("gdelt_geo_fetch_failed", error=str(e))
            return []


def normalize_gdelt_geo(feature: Dict) -> Optional[Event]:
    try:
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [0, 0])
        
        themes = props.get("Themes", "").split(";") if props.get("Themes") else []
        locations = props.get("Locations", "").split(";") if props.get("Locations") else []
        
        severity = 0.3
        if any(t in ["TAX", "WAR", "DISASTER", "PROTEST"] for t in themes):
            severity = 0.7
        elif any(t in ["ECON", "HEALTH", "ENVIRONMENT"] for t in themes):
            severity = 0.4
        
        return Event(
            source="gdelt_geo",
            domain="geopolitical",
            event_type="gdelt_event",
            severity=severity,
            geometry={"type": "Point", "coordinates": coords},
            properties={
                "global_event_id": props.get("GlobalEventID"),
                "date": props.get("Date"),
                "actor1": props.get("Actor1Name"),
                "actor2": props.get("Actor2Name"),
                "event_code": props.get("EventCode"),
                "event_base_code": props.get("EventBaseCode"),
                "event_root_code": props.get("EventRootCode"),
                "quad_class": props.get("QuadClass"),
                "goldstein_scale": props.get("GoldsteinScale"),
                "num_mentions": props.get("NumMentions"),
                "num_sources": props.get("NumSources"),
                "num_articles": props.get("NumArticles"),
                "avg_tone": props.get("AvgTone"),
                "actor1_country": props.get("Actor1CountryCode"),
                "actor2_country": props.get("Actor2CountryCode"),
                "action_country": props.get("ActionCountryCode"),
                "themes": themes,
                "locations": locations,
            },
            metadata={
                "severity_tier": "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low",
            },
            timestamp=props.get("Date", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("gdelt_geo_normalize_failed", error=str(e))
        return None