import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


OPEN_NOTIFY_BASE_URL = "http://api.open-notify.org"


async def fetch_iss_position() -> Optional[Dict]:
    url = f"{OPEN_NOTIFY_BASE_URL}/iss-now.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("open_notify_iss_fetch_failed", error=str(e))
            return None


async def fetch_iss_passes(lat: float, lon: float, alt: float = 0, n: int = 5) -> List[Dict]:
    url = f"{OPEN_NOTIFY_BASE_URL}/iss-pass.json"
    params = {"lat": lat, "lon": lon, "alt": alt, "n": n}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", [])
        except Exception as e:
            logger.error("open_notify_passes_fetch_failed", error=str(e))
            return []


async def fetch_astronauts() -> List[Dict]:
    url = f"{OPEN_NOTIFY_BASE_URL}/astros.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return data.get("people", [])
        except Exception as e:
            logger.error("open_notify_astronauts_fetch_failed", error=str(e))
            return []


def normalize_iss_position(data: Dict) -> Optional[Event]:
    try:
        position = data.get("iss_position", {})
        lat = float(position.get("latitude", 0))
        lon = float(position.get("longitude", 0))
        timestamp = data.get("timestamp", 0)
        
        return Event(
            source="open_notify",
            domain="space",
            event_type="iss_position",
            severity=0.2,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            properties={
                "message": data.get("message"),
                "altitude_km": 408,
                "velocity_kmh": 27600,
            },
            metadata={"severity_tier": "low"},
            timestamp=datetime.fromtimestamp(timestamp).isoformat() if timestamp else datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("open_notify_iss_normalize_failed", error=str(e))
        return None


def normalize_astronauts(data: List[Dict]) -> Optional[Event]:
    try:
        count = len(data)
        crafts = list(set(p.get("craft") for p in data))
        
        return Event(
            source="open_notify",
            domain="space",
            event_type="astronauts_in_space",
            severity=0.1,
            geometry={"type": "Point", "coordinates": [0, 0]},
            properties={
                "count": count,
                "astronauts": data,
                "crafts": crafts,
            },
            metadata={"severity_tier": "info"},
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("open_notify_astronauts_normalize_failed", error=str(e))
        return None