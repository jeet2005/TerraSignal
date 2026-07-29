import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.event import Event
from app.core.logging import logger


OPENAQ_BASE_URL = "https://api.openaq.org/v2"


def calculate_severity(domain: str, aqi: int) -> float:
    if domain == "air_quality":
        if aqi >= 300:
            return 1.0
        elif aqi >= 200:
            return 0.8
        elif aqi >= 150:
            return 0.6
        elif aqi >= 100:
            return 0.4
        elif aqi >= 50:
            return 0.2
        else:
            return 0.1
    return 0.1


async def fetch_openaq_measurements(lat: float, lon: float, radius: int = 50000) -> List[Dict]:
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": radius,
        "limit": 100,
        "order_by": "lastUpdated",
        "sort": "desc",
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(f"{OPENAQ_BASE_URL}/latest", params=params)
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception as e:
            logger.error("openaq_fetch_failed", error=str(e), lat=lat, lon=lon)
            return []


def normalize_openaq_event(station: Dict, lat: float, lon: float) -> Optional[Event]:
    try:
        measurements = station.get("measurements", [])
        aqi_values = []
        pollutants = {}
        
        for m in measurements:
            param = m.get("parameter")
            value = m.get("value")
            if value is not None:
                pollutants[param.lower()] = value
                if param in ["pm25", "pm10", "no2", "o3", "so2", "co"]:
                    aqi = calculate_aqi(param, value)
                    aqi_values.append(aqi)
        
        overall_aqi = max(aqi_values) if aqi_values else 0
        severity = calculate_severity("air_quality", overall_aqi)
        
        return Event(
            source="openaq",
            domain="air_quality",
            event_type="aqi_reading",
            severity=severity,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            properties={
                "station_id": station.get("locationId"),
                "station_name": station.get("location"),
                "aqi": overall_aqi,
                "pollutants": pollutants,
                "last_updated": station.get("lastUpdated"),
            },
            metadata={
                "severity_tier": "critical" if severity >= 0.8 else "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("openaq_normalize_failed", error=str(e))
        return None


def calculate_aqi(param: str, value: float) -> int:
    if param == "pm25":
        if value <= 12: return int(value * 50 / 12)
        elif value <= 35.4: return int(50 + (value - 12.1) * 50 / (35.4 - 12.1))
        elif value <= 55.4: return int(100 + (value - 35.5) * 50 / (55.4 - 35.5))
        elif value <= 150.4: return int(150 + (value - 55.5) * 100 / (150.4 - 55.5))
        elif value <= 250.4: return int(200 + (value - 150.5) * 100 / (250.4 - 150.5))
        else: return int(300 + (value - 250.5) * 200 / (500.4 - 250.5))
    elif param == "pm10":
        if value <= 54: return int(value * 50 / 54)
        elif value <= 154: return int(50 + (value - 55) * 50 / (154 - 55))
        elif value <= 254: return int(100 + (value - 155) * 50 / (254 - 155))
        elif value <= 354: return int(150 + (value - 255) * 100 / (354 - 255))
        elif value <= 424: return int(200 + (value - 355) * 100 / (424 - 355))
        else: return int(300 + (value - 425) * 200 / (604 - 425))
    elif param == "no2":
        if value <= 53: return int(value * 50 / 53)
        elif value <= 100: return int(50 + (value - 54) * 50 / (100 - 54))
        elif value <= 360: return int(100 + (value - 101) * 50 / (360 - 101))
        elif value <= 649: return int(150 + (value - 361) * 100 / (649 - 361))
        elif value <= 1249: return int(200 + (value - 650) * 100 / (1249 - 650))
        else: return int(300 + (value - 1250) * 200 / (2049 - 1250))
    elif param == "o3":
        if value <= 54: return int(value * 50 / 54)
        elif value <= 70: return int(50 + (value - 55) * 50 / (70 - 55))
        elif value <= 85: return int(100 + (value - 71) * 50 / (85 - 71))
        elif value <= 105: return int(150 + (value - 86) * 100 / (105 - 86))
        elif value <= 200: return int(200 + (value - 106) * 100 / (200 - 106))
        else: return 300
    return 0