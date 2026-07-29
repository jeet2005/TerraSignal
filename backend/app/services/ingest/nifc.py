import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


NIFC_BASE_URL = "https://services.nifc.gov/arcgis/rest/services/Wildfire/Current_Perimeters/FeatureServer/0/query"


def calculate_severity(domain: str, **kwargs) -> float:
    if domain == "fire":
        acres = kwargs.get("acres", 0)
        if acres >= 100000:
            return 1.0
        elif acres >= 50000:
            return 0.8
        elif acres >= 10000:
            return 0.6
        elif acres >= 1000:
            return 0.4
        elif acres >= 100:
            return 0.2
        else:
            return 0.1
    return 0.1


async def fetch_nifc_fires() -> List[Dict]:
    params = {
        "where": "1=1",
        "outFields": "*",
        "f": "geojson",
        "returnGeometry": "true",
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(NIFC_BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("features", [])
        except Exception as e:
            logger.error("nifc_fetch_failed", error=str(e))
            return []


def normalize_nifc_fire(feature: Dict) -> Optional[Event]:
    try:
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        
        acres = props.get("GIS_ACRES", 0)
        severity = calculate_severity("fire", acres=acres)
        
        coordinates = geom.get("coordinates", [])
        if geom.get("type") == "Polygon" and coordinates:
            centroid = calculate_polygon_centroid(coordinates[0])
            lon, lat = centroid
        elif geom.get("type") == "MultiPolygon" and coordinates:
            lon, lat = coordinates[0][0][0]
        else:
            lon, lat = 0, 0
        
        return Event(
            source="nifc",
            domain="fire",
            event_type="wildfire_perimeter",
            severity=severity,
            geometry=geom,
            properties={
                "fire_name": props.get("FIRE_NAME"),
                "incident_id": props.get("INCIDENT_ID"),
                "acres": acres,
                "percent_contained": props.get("PERCENT_CONTAINED"),
                "fire_discovery_date": props.get("FIRE_DISCOVERY_DATE"),
                "cause": props.get("CAUSE"),
                "state": props.get("STATE"),
                "county": props.get("COUNTY"),
                "responsible_agency": props.get("RESPONSIBLE_AGENCY"),
            },
            metadata={
                "severity_tier": "critical" if severity >= 0.8 else "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("nifc_normalize_failed", error=str(e))
        return None


def calculate_polygon_centroid(coords: List[List[float]]) -> tuple:
    if not coords:
        return (0, 0)
    x = sum(c[0] for c in coords) / len(coords)
    y = sum(c[1] for c in coords) / len(coords)
    return (x, y)