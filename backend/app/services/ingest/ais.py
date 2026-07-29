import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


AIS_BASE_URL = "https://api.ais.52north.org"


def calculate_severity(domain: str, **kwargs) -> float:
    if domain == "maritime":
        vessel_type = kwargs.get("vessel_type", 0)
        speed = kwargs.get("speed", 0)
        
        if vessel_type >= 30 and vessel_type <= 39:
            base = 0.15
        elif vessel_type >= 50 and vessel_type <= 59:
            base = 0.25
        elif vessel_type >= 60 and vessel_type <= 69:
            base = 0.3
        elif vessel_type >= 70 and vessel_type <= 79:
            base = 0.35
        elif vessel_type >= 80 and vessel_type <= 89:
            base = 0.4
        elif vessel_type >= 90:
            base = 0.45
        elif vessel_type >= 20 and vessel_type <= 29:
            base = 0.2
        else:
            base = 0.1
        
        speed_factor = min(speed / 50, 0.2)
        return min(base + speed_factor, 0.5)
    return 0.1


async def fetch_ais_vessels(bbox: str = "-180,-90,180,90") -> List[Dict]:
    url = f"{AIS_BASE_URL}/positions"
    params = {"bbox": bbox}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("ais_fetch_failed", error=str(e))
            return []


def normalize_ais_vessel(vessel: Dict) -> Optional[Event]:
    try:
        mmsi = vessel.get("mmsi")
        lat = vessel.get("lat")
        lon = vessel.get("lon")
        
        if lat is None or lon is None:
            return None
        
        vessel_type = vessel.get("shiptype", 0)
        speed = vessel.get("sog", 0)
        severity = calculate_severity("maritime", vessel_type=vessel_type, speed=speed)
        
        return Event(
            source="ais",
            domain="maritime",
            event_type="vessel_position",
            severity=severity,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            properties={
                "mmsi": mmsi,
                "imo": vessel.get("imo"),
                "name": vessel.get("name"),
                "callsign": vessel.get("callsign"),
                "vessel_type": vessel_type,
                "length": vessel.get("length"),
                "width": vessel.get("width"),
                "draft": vessel.get("draught"),
                "speed": speed,
                "course": vessel.get("cog"),
                "heading": vessel.get("heading"),
                "destination": vessel.get("destination"),
                "eta": vessel.get("eta"),
                "nav_status": vessel.get("navstatus"),
            },
            metadata={
                "severity_tier": "low" if severity < 0.2 else "moderate" if severity < 0.4 else "high",
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("ais_normalize_failed", error=str(e))
        return None


async def fetch_ais_all() -> List[Dict]:
    return await fetch_ais_vessels()