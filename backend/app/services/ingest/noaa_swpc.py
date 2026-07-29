import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


NOAA_SWPC_BASE_URL = "https://services.swpc.noaa.gov/json"


def calculate_severity(domain: str, **kwargs) -> float:
    if domain == "space_weather":
        event_type = kwargs.get("event_type", "").lower()
        if "x-class" in event_type or "extreme" in event_type:
            return 1.0
        elif "m-class" in event_type or "major" in event_type:
            return 0.8
        elif "c-class" in event_type or "moderate" in event_type:
            return 0.5
        elif "minor" in event_type or "g1" in event_type:
            return 0.3
        elif "kp" in event_type:
            kp = kwargs.get("kp_index", 0)
            if kp >= 8:
                return 0.9
            elif kp >= 6:
                return 0.7
            elif kp >= 4:
                return 0.4
            else:
                return 0.2
    return 0.1


async def fetch_solar_flares() -> List[Dict]:
    url = f"{NOAA_SWPC_BASE_URL}/solar-flares.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("swpc_flares_fetch_failed", error=str(e))
            return []


async def fetch_geomagnetic_storms() -> List[Dict]:
    url = f"{NOAA_SWPC_BASE_URL}/planetary-k-index.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return data[1:] if len(data) > 1 else []
        except Exception as e:
            logger.error("swpc_kp_fetch_failed", error=str(e))
            return []


async def fetch_solar_wind() -> List[Dict]:
    url = f"{NOAA_SWPC_BASE_URL}/solar-wind/mag-1-day.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return data[1:] if len(data) > 1 else []
        except Exception as e:
            logger.error("swpc_solar_wind_fetch_failed", error=str(e))
            return []


async def fetch_aurora_forecast() -> List[Dict]:
    url = f"{NOAA_SWPC_BASE_URL}/ovation-aurora.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("swpc_aurora_fetch_failed", error=str(e))
            return []


def normalize_solar_flare(flare: Dict) -> Optional[Event]:
    try:
        class_type = flare.get("classType", "")
        severity = calculate_severity("space_weather", event_type=class_type)
        
        return Event(
            source="noaa_swpc",
            domain="space_weather",
            event_type="solar_flare",
            severity=severity,
            geometry={"type": "Point", "coordinates": [0, 0]},
            properties={
                "class_type": class_type,
                "begin_time": flare.get("beginTime"),
                "peak_time": flare.get("peakTime"),
                "end_time": flare.get("endTime"),
                "source_location": flare.get("sourceLocation"),
                "active_region": flare.get("activeRegionNum"),
                "flux": flare.get("flux"),
            },
            metadata={
                "severity_tier": "critical" if severity >= 0.8 else "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
            },
            timestamp=flare.get("peakTime", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("swpc_flare_normalize_failed", error=str(e))
        return None


def normalize_kp_index(kp_data: Dict) -> Optional[Event]:
    try:
        kp = float(kp_data.get("kp_index", 0))
        severity = calculate_severity("space_weather", event_type="kp", kp_index=kp)
        
        return Event(
            source="noaa_swpc",
            domain="space_weather",
            event_type="geomagnetic_storm",
            severity=severity,
            geometry={"type": "Point", "coordinates": [0, 0]},
            properties={
                "kp_index": kp,
                "observed_time": kp_data.get("observed_time"),
                "source": kp_data.get("source"),
            },
            metadata={
                "severity_tier": "critical" if severity >= 0.8 else "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
            },
            timestamp=kp_data.get("observed_time", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("swpc_kp_normalize_failed", error=str(e))
        return None


async def fetch_noaa_swpc_all() -> Dict:
    flares = await fetch_solar_flares()
    kp = await fetch_geomagnetic_storms()
    return {"flares": flares, "kp": kp}