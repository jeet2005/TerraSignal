import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.event import Event
from app.core.logging import logger
from app.core.config import settings


OPENSKY_BASE_URL = "https://opensky-network.org/api"


def calculate_severity(domain: str, **kwargs) -> float:
    if domain == "aviation":
        altitude = kwargs.get("altitude", 0)
        velocity = kwargs.get("velocity", 0)
        on_ground = kwargs.get("on_ground", False)
        if on_ground:
            return 0.01
        if altitude > 12000:
            return 0.1
        elif altitude > 3000:
            return 0.05
        return 0.02
    return 0.01


async def fetch_opensky_states(
    lamin: float = None,
    lomin: float = None,
    lamax: float = None,
    lomax: float = None
) -> List[Dict]:
    url = f"{OPENSKY_BASE_URL}/states/all"
    params = {}
    if lamin is not None:
        params["lamin"] = lamin
        params["lomin"] = lomin
        params["lamax"] = lamax
        params["lomax"] = lomax
    
    auth = None
    if settings.OPENSKY_USERNAME and settings.OPENSKY_PASSWORD:
        auth = (settings.OPENSKY_USERNAME, settings.OPENSKY_PASSWORD)
    
    async with httpx.AsyncClient(timeout=30.0, auth=auth) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            states = data.get("states", [])
            return states
        except Exception as e:
            logger.error("opensky_fetch_failed", error=str(e))
            return []


async def fetch_opensky_flight(icao24: str) -> Optional[Dict]:
    url = f"{OPENSKY_BASE_URL}/tracks/all"
    params = {"icao24": icao24}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("opensky_track_fetch_failed", error=str(e))
            return None


def normalize_opensky_state(state: List) -> Optional[Event]:
    try:
        if not state or len(state) < 17:
            return None
        
        icao24 = state[0]
        callsign = state[1].strip() if state[1] else None
        origin_country = state[2]
        time_position = state[3]
        last_contact = state[4]
        lon = state[5]
        lat = state[6]
        baro_altitude = state[7]
        on_ground = state[8]
        velocity = state[9]
        true_track = state[10]
        vertical_rate = state[11]
        sensors = state[12]
        geo_altitude = state[13]
        squawk = state[14]
        spi = state[15]
        position_source = state[16]
        
        if lat is None or lon is None:
            return None
        
        altitude = geo_altitude or baro_altitude or 0
        severity = calculate_severity("aviation", altitude=altitude, velocity=velocity or 0, on_ground=on_ground)
        
        return Event(
            source="opensky",
            domain="aviation",
            event_type="flight_position",
            severity=severity,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            properties={
                "icao24": icao24,
                "callsign": callsign,
                "origin_country": origin_country,
                "altitude": altitude,
                "baro_altitude": baro_altitude,
                "on_ground": on_ground,
                "velocity": velocity,
                "true_track": true_track,
                "vertical_rate": vertical_rate,
                "squawk": squawk,
                "spi": spi,
                "position_source": position_source,
            },
            metadata={
                "severity_tier": "info",
            },
            timestamp=datetime.fromtimestamp(time_position).isoformat() if time_position else datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("opensky_normalize_failed", error=str(e))
        return None


async def fetch_opensky_all() -> List[Dict]:
    return await fetch_opensky_states()