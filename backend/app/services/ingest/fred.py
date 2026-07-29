import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger
from app.core.config import settings


FRED_BASE_URL = "https://api.stlouisfed.org/fred"


async def fetch_fred_series(
    series_id: str,
    api_key: str = None,
    limit: int = 100
) -> List[Dict]:
    url = f"{FRED_BASE_URL}/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key or settings.FRED_API_KEY,
        "file_type": "json",
        "limit": limit,
        "sort_order": "desc",
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("observations", [])
        except Exception as e:
            logger.error("fred_series_fetch_failed", error=str(e), series_id=series_id)
            return []


async def fetch_fred_series_search(search_text: str, api_key: str = None) -> List[Dict]:
    url = f"{FRED_BASE_URL}/series/search"
    params = {
        "search_text": search_text,
        "api_key": api_key or settings.FRED_API_KEY,
        "file_type": "json",
        "limit": 50,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("seriess", [])
        except Exception as e:
            logger.error("fred_search_failed", error=str(e))
            return []


async def fetch_fred_releases(api_key: str = None) -> List[Dict]:
    url = f"{FRED_BASE_URL}/releases"
    params = {"api_key": api_key or settings.FRED_API_KEY, "file_type": "json"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("releases", [])
        except Exception as e:
            logger.error("fred_releases_fetch_failed", error=str(e))
            return []


FRED_KEY_SERIES = {
    "GDP": "Gross Domestic Product",
    "UNRATE": "Unemployment Rate",
    "CPIAUCSL": "Consumer Price Index",
    "FEDFUNDS": "Federal Funds Rate",
    "DGS10": "10-Year Treasury Rate",
    "DEXUSEU": "USD/EUR Exchange Rate",
    "DEXUSUK": "USD/GBP Exchange Rate",
    "DEXJPUS": "JPY/USD Exchange Rate",
    "INDPRO": "Industrial Production Index",
    "PAYEMS": "Total Nonfarm Payrolls",
}


def normalize_fred_observation(obs: Dict, series_id: str, series_name: str) -> Optional[Event]:
    try:
        value = obs.get("value")
        date = obs.get("date")
        
        if value == "." or value is None:
            return None
        
        value = float(value)
        
        return Event(
            source="fred",
            domain="economics",
            event_type="indicator",
            severity=0.2,
            geometry={"type": "Point", "coordinates": [-98.5795, 39.8283]},  # US center
            properties={
                "series_id": series_id,
                "series_name": series_name,
                "value": value,
                "date": date,
                "unit": "varies",
            },
            metadata={"severity_tier": "info"},
            timestamp=datetime.fromisoformat(date).isoformat() if date else datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("fred_normalize_failed", error=str(e))
        return None