import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.event import Event
from app.core.logging import logger


OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"


def calculate_severity(domain: str, value: float) -> float:
    if domain == "weather":
        if value >= 50:
            return 0.8
        elif value >= 30:
            return 0.6
        elif value >= 15:
            return 0.4
        else:
            return 0.2
    return 0.1


async def fetch_open_meteo_weather(lat: float, lon: float) -> Optional[Dict]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m",
        "hourly": "temperature_2m,precipitation_probability,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 2,
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(OPEN_METEO_BASE_URL, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("open_meteo_fetch_failed", error=str(e), lat=lat, lon=lon)
            return None


def normalize_weather_event(data: Dict, lat: float, lon: float, city: str = None, country: str = None) -> Optional[Event]:
    try:
        current = data.get("current", {})
        weather_code = current.get("weather_code", 0)
        
        severity = 0.1
        if weather_code in [95, 96, 99]:
            severity = 0.8
        elif weather_code in [56, 57, 66, 67, 75, 77, 82, 86]:
            severity = 0.6
        elif weather_code in [51, 53, 55, 61, 63, 65, 71, 73, 80, 81]:
            severity = 0.4
        elif weather_code in [1, 2, 3, 45, 48]:
            severity = 0.2
        
        return Event(
            source="open-meteo",
            domain="weather",
            event_type="weather_condition",
            severity=severity,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            properties={
                "temperature": current.get("temperature_2m"),
                "apparent_temperature": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "weather_code": weather_code,
                "hourly": data.get("hourly"),
                "daily": data.get("daily"),
            },
            metadata={
                "severity_tier": "critical" if severity >= 0.8 else "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
                "city": city,
                "country": country,
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("open_meteo_normalize_failed", error=str(e))
        return None