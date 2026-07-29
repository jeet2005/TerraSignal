import httpx
from datetime import datetime
from typing: Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


CLOUDFLARE_RADAR_URL = "https://radar.cloudflare.com/api"


async def fetch_cloudflare_outages() -> List[Dict]:
    url = f"{CLOUDFLARE_RADAR_URL}/outages"
    params = {"limit": 100}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("result", [])
        except Exception as e:
            logger.error("cloudflare_outages_fetch_failed", error=str(e))
            return []


async def fetch_cloudflare_internet_quality() -> Optional[Dict]:
    url = f"{CLOUDFLARE_RADAR_URL}/internet-quality"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("cloudflare_quality_fetch_failed", error=str(e))
            return None


async def fetch_cloudflare_traffic(country: str = None) -> Optional[Dict]:
    url = f"{CLOUDFLARE_RADAR_URL}/traffic"
    params = {}
    if country:
        params["country"] = country
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("cloudflare_traffic_fetch_failed", error=str(e))
            return None


def normalize_cloudflare_outage(outage: Dict) -> Optional[Event]:
    try:
        lat = outage.get("location", {}).get("latitude")
        lon = outage.get("location", {}).get("longitude")
        
        coords = [0, 0]
        if lat is not None and lon is not None:
            coords = [float(lon), float(lat)]
        
        severity = 0.3
        if outage.get("impact") == "high":
            severity = 0.7
        elif outage.get("impact") == "medium":
            severity = 0.5
        
        return Event(
            source="cloudflare_radar",
            domain="digital",
            event_type="internet_outage",
            severity=severity,
            geometry={"type": "Point", "coordinates": coords},
            properties={
                "outage_id": outage.get("id"),
                "start_time": outage.get("start_time"),
                "end_time": outage.get("end_time"),
                "duration": outage.get("duration"),
                "impact": outage.get("impact"),
                "asn": outage.get("asn"),
                "asn_name": outage.get("asn_name"),
                "country_code": outage.get("country_code"),
                "country_name": outage.get("country_name"),
                "description": outage.get("description"),
            },
            metadata={
                "severity_tier": "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low",
            },
            timestamp=outage.get("start_time", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("cloudflare_outage_normalize_failed", error=str(e))
        return None