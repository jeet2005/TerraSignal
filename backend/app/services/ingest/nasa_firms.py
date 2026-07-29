import httpx
from datetime import datetime
from typing import List, Dict, Optional
from app.models.event import Event
from app.core.logging import logger


NASA_FIRMS_BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"


def calculate_severity(domain: str, **kwargs) -> float:
    if domain == "fire":
        confidence = kwargs.get("confidence", "l")
        frp = kwargs.get("frp", 0)
        conf_map = {"l": 0.3, "n": 0.6, "h": 0.9}
        base = conf_map.get(confidence.lower(), 0.3)
        frp_factor = min(frp / 1000, 0.3)
        return min(base + frp_factor, 1.0)
    return 0.1


async def fetch_nasa_firms(bbox: List[float] = None) -> List[Dict]:
    if bbox is None:
        bbox = [-180, -90, 180, 90]
    
    params = {
        "area": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "day": 1,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(NASA_FIRMS_BASE_URL, params=params)
            resp.raise_for_status()
            lines = resp.text.strip().split("\n")
            if len(lines) < 2:
                return []
            headers = lines[0].split(",")
            fires = []
            for line in lines[1:]:
                values = line.split(",")
                if len(values) == len(headers):
                    fires.append(dict(zip(headers, values)))
            return fires
        except Exception as e:
            logger.error("nasa_firms_fetch_failed", error=str(e))
            return []


def normalize_firms_event(fire: Dict) -> Optional[Event]:
    try:
        lat = float(fire.get("latitude", 0))
        lon = float(fire.get("longitude", 0))
        confidence = fire.get("confidence", "l")
        frp = float(fire.get("frp", 0))
        
        severity = calculate_severity("fire", confidence=confidence, frp=frp)
        
        return Event(
            source="nasa_firms",
            domain="fire",
            event_type="fire_hotspot",
            severity=severity,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            properties={
                "brightness": float(fire.get("brightness", 0)),
                "scan": float(fire.get("scan", 0)),
                "track": float(fire.get("track", 0)),
                "acq_date": fire.get("acq_date"),
                "acq_time": fire.get("acq_time"),
                "satellite": fire.get("satellite"),
                "instrument": fire.get("instrument"),
                "confidence": confidence,
                "version": fire.get("version"),
                "bright_t31": float(fire.get("bright_t31", 0)),
                "frp": frp,
                "daynight": fire.get("daynight"),
            },
            metadata={
                "severity_tier": "critical" if severity >= 0.8 else "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("nasa_firms_normalize_failed", error=str(e))
        return None