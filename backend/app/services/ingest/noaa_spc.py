import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


NOAA_SPC_BASE_URL = "https://www.spc.noaa.gov/products/outlook/archive"


def calculate_severity(domain: str, **kwargs) -> float:
    if domain == "weather":
        risk = kwargs.get("risk_level", "").lower()
        if "high" in risk:
            return 1.0
        elif "moderate" in risk:
            return 0.7
        elif "enhanced" in risk:
            return 0.5
        elif "slight" in risk:
            return 0.3
        elif "marginal" in risk:
            return 0.2
        else:
            return 0.1
    return 0.1


async def fetch_noaa_spc_outlook(day: int = 1) -> List[Dict]:
    url = f"{NOAA_SPC_BASE_URL}/day{day}otlk_{datetime.utcnow().strftime('%Y%m%d')}_1200.txt"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 404:
                url = f"{NOAA_SPC_BASE_URL}/day{day}otlk_{datetime.utcnow().strftime('%Y%m%d')}_0600.txt"
                resp = await client.get(url)
            resp.raise_for_status()
            return parse_spc_outlook(resp.text)
        except Exception as e:
            logger.error("noaa_spc_fetch_failed", error=str(e))
            return []


def parse_spc_outlook(text: str) -> List[Dict]:
    outlooks = []
    lines = text.split('\n')
    current_area = None
    current_risk = None
    
    for line in lines:
        line = line.strip()
        if line.startswith("."):
            continue
        if "RISK" in line.upper():
            parts = line.split()
            if len(parts) >= 2:
                current_risk = " ".join(parts[1:])
        elif line and not line.startswith(".") and len(line) > 10:
            current_area = line
            outlooks.append({
                "area": current_area,
                "risk_level": current_risk or "None",
                "day": 1,
            })
    return outlooks


async def fetch_noaa_spc_all() -> List[Dict]:
    all_outlooks = []
    for day in [1, 2, 3]:
        outlooks = await fetch_noaa_spc_outlook(day)
        all_outlooks.extend(outlooks)
    return all_outlooks


def normalize_noaa_spc_event(outlook: Dict) -> Optional[Event]:
    try:
        risk = outlook.get("risk_level", "")
        severity = calculate_severity("weather", risk_level=risk)
        
        return Event(
            source="noaa_spc",
            domain="weather",
            event_type="storm_outlook",
            severity=severity,
            geometry={"type": "Point", "coordinates": [-98.5, 39.8]},
            properties={
                "area": outlook.get("area"),
                "risk_level": risk,
                "day": outlook.get("day"),
                "hazards": ["tornado", "hail", "wind"],
            },
            metadata={
                "severity_tier": "critical" if severity >= 0.8 else "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("noaa_spc_normalize_failed", error=str(e))
        return None