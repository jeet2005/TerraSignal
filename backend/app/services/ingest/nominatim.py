import httpx
from datetime import datetime
from typing: Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"


async def geocode(query: str, limit: int = 10) -> List[Dict]:
    url = f"{NOMINATIM_BASE_URL}/search"
    params = {
        "q": query,
        "format": "json",
        "limit": limit,
        "addressdetails": 1,
        "extratags": 1,
        "namedetails": 1,
    }
    
    headers = {"User-Agent": "TerraSignal/1.0"}
    
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("nominatim_geocode_failed", error=str(e), query=query)
            return []


async def reverse_geocode(lat: float, lon: float) -> Optional[Dict]:
    url = f"{NOMINATIM_BASE_URL}/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
        "extratags": 1,
        "namedetails": 1,
    }
    
    headers = {"User-Agent": "TerraSignal/1.0"}
    
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("nominatim_reverse_failed", error=str(e), lat=lat, lon=lon)
            return None


async def geocode_batch(queries: List[str]) -> List[List[Dict]]:
    results = []
    for query in queries:
        result = await geocode(query)
        results.append(result)
    return results


def normalize_nominatim_result(result: Dict) -> Optional[Event]:
    try:
        lat = float(result.get("lat", 0))
        lon = float(result.get("lon", 0))
        
        return Event(
            source="nominatim",
            domain="geocoding",
            event_type="geocode_result",
            severity=0.01,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            properties={
                "place_id": result.get("place_id"),
                "licence": result.get("licence"),
                "osm_type": result.get("osm_type"),
                "osm_id": result.get("osm_id"),
                "display_name": result.get("display_name"),
                "place_rank": result.get("place_rank"),
                "category": result.get("category"),
                "type": result.get("type"),
                "importance": result.get("importance"),
                "address": result.get("address"),
                "extratags": result.get("extratags"),
                "namedetails": result.get("namedetails"),
            },
            metadata={"severity_tier": "info"},
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("nominatim_normalize_failed", error=str(e))
        return None