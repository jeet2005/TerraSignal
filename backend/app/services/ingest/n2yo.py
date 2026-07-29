import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


N2YO_BASE_URL = "https://api.n2yo.com/rest/v1/satellite"


async def fetch_n2yo_above(
    lat: float,
    lon: float,
    alt: float,
    radius: int,
    category: int,
    api_key: str
) -> List[Dict]:
    url = f"{N2YO_BASE_URL}/above/{lat}/{lon}/{alt}/{radius}/{category}"
    params = {"apiKey": api_key}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("above", [])
        except Exception as e:
            logger.error("n2yo_above_fetch_failed", error=str(e))
            return []


async def fetch_n2yo_positions(
    sat_id: int,
    lat: float,
    lon: float,
    alt: float,
    seconds: int,
    api_key: str
) -> List[Dict]:
    url = f"{N2YO_BASE_URL}/positions/{sat_id}/{lat}/{lon}/{alt}/{seconds}"
    params = {"apiKey": api_key}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("positions", [])
        except Exception as e:
            logger.error("n2yo_positions_fetch_failed", error=str(e))
            return []


async def fetch_n2yo_tle(sat_id: int, api_key: str) -> Optional[Dict]:
    url = f"{N2YO_BASE_URL}/tle/{sat_id}"
    params = {"apiKey": api_key}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("tle")
        except Exception as e:
            logger.error("n2yo_tle_fetch_failed", error=str(e))
            return None


def normalize_n2yo_satellite(sat: Dict) -> Optional[Event]:
    try:
        sat_lat = sat.get("satlat")
        sat_lon = sat.get("satlng")
        sat_alt = sat.get("satalt")
        
        if sat_lat is None or sat_lon is None:
            return None
        
        return Event(
            source="n2yo",
            domain="space",
            event_type="satellite_position",
            severity=0.1,
            geometry={"type": "Point", "coordinates": [float(sat_lon), float(sat_lat)]},
            properties={
                "sat_id": sat.get("satid"),
                "sat_name": sat.get("satname"),
                "int_designator": sat.get("intDesignator"),
                "launch_date": sat.get("launchDate"),
                "latitude": float(sat_lat),
                "longitude": float(sat_lon),
                "altitude_km": float(sat_alt) if sat_alt else 0,
                "velocity_kms": float(sat.get("velocity", 0)) if sat.get("velocity") else 0,
                "azimuth": float(sat.get("azimuth", 0)) if sat.get("azimuth") else 0,
                "elevation": float(sat.get("elevation", 0)) if sat.get("elevation") else 0,
                "footprint": sat.get("footprint"),
                "range_km": sat.get("range"),
            },
            metadata={"severity_tier": "info"},
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("n2yo_normalize_failed", error=str(e))
        return None