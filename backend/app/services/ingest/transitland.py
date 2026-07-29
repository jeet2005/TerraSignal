import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


TRANSITLAND_BASE_URL = "https://transit.land/api/v2/rest"


async def fetch_transitland_feeds(
    limit: int = 100,
    offset: int = 0
) -> List[Dict]:
    url = f"{TRANSITLAND_BASE_URL}/feeds"
    params = {"limit": limit, "offset": offset}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("feeds", [])
        except Exception as e:
            logger.error("transitland_feeds_fetch_failed", error=str(e))
            return []


async def fetch_transitland_operators(
    limit: int = 100
) -> List[Dict]:
    url = f"{TRANSITLAND_BASE_URL}/operators"
    params = {"limit": limit}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("operators", [])
        except Exception as e:
            logger.error("transitland_operators_fetch_failed", error=str(e))
            return []


async def fetch_transitland_stops(
    lat: float,
    lon: float,
    radius: int = 5000
) -> List[Dict]:
    url = f"{TRANSITLAND_BASE_URL}/stops"
    params = {"lat": lat, "lon": lon, "r": radius, "limit": 100}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("stops", [])
        except Exception as e:
            logger.error("transitland_stops_fetch_failed", error=str(e))
            return []


def normalize_transitland_feed(feed: Dict) -> Optional[Event]:
    try:
        lat = feed.get("feed", {}).get("location", {}).get("lat")
        lon = feed.get("feed", {}).get("location", {}).get("lon")
        
        coords = [0, 0]
        if lat is not None and lon is not None:
            coords = [float(lon), float(lat)]
        
        return Event(
            source="transitland",
            domain="transit",
            event_type="gtfs_feed",
            severity=0.1,
            geometry={"type": "Point", "coordinates": coords},
            properties={
                "feed_id": feed.get("feed", {}).get("id"),
                "feed_name": feed.get("feed", {}).get("name"),
                "feed_url": feed.get("feed", {}).get("url"),
                "license": feed.get("feed", {}).get("license"),
                "operator_name": feed.get("operator", {}).get("name"),
                "operator_id": feed.get("operator", {}).get("id"),
                "location": feed.get("feed", {}).get("location"),
            },
            metadata={"severity_tier": "info"},
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("transitland_feed_normalize_failed", error=str(e))
        return None


def normalize_transitland_operator(operator: Dict) -> Optional[Event]:
    try:
        lat = operator.get("location", {}).get("lat")
        lon = operator.get("location", {}).get("lon")
        
        coords = [0, 0]
        if lat is not None and lon is not None:
            coords = [float(lon), float(lat)]
        
        return Event(
            source="transitland",
            domain="transit",
            event_type="operator",
            severity=0.1,
            geometry={"type": "Point", "coordinates": coords},
            properties={
                "operator_id": operator.get("id"),
                "name": operator.get("name"),
                "short_name": operator.get("short_name"),
                "website": operator.get("website"),
                "phone": operator.get("phone"),
                "location": operator.get("location"),
                "timezone": operator.get("timezone"),
            },
            metadata={"severity_tier": "info"},
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("transitland_operator_normalize_failed", error=str(e))
        return None