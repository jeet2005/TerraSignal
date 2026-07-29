import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


COMMODITY_BASE_URL = "https://api.commodityprices.com/v1"


async def fetch_commodity_prices(
    symbols: List[str] = None,
    api_key: str = None
) -> List[Dict]:
    url = f"{COMMODITY_BASE_URL}/latest"
    params = {}
    if symbols:
        params["symbols"] = ",".join(symbols)
    if api_key:
        params["api_key"] = api_key
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            logger.error("commodity_fetch_failed", error=str(e))
            return []


async def fetch_commodity_historical(
    symbol: str,
    start_date: str,
    end_date: str,
    api_key: str = None
) -> List[Dict]:
    url = f"{COMMODITY_BASE_URL}/historical"
    params = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
    }
    if api_key:
        params["api_key"] = api_key
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            logger.error("commodity_historical_fetch_failed", error=str(e))
            return []


COMMODITY_CATEGORIES = {
    "energy": ["CL", "NG", "RB", "HO", "BZ"],
    "metals": ["GC", "SI", "HG", "PL", "PA"],
    "agriculture": ["ZC", "ZW", "ZS", "KC", "CT", "SB"],
    "livestock": ["LE", "HE", "GF"],
}


def normalize_commodity_price(commodity: Dict) -> Optional[Event]:
    try:
        symbol = commodity.get("symbol")
        price = commodity.get("price")
        change = commodity.get("change", 0)
        change_pct = commodity.get("change_percent", 0)
        
        severity = min(abs(change_pct) / 50, 0.5)
        
        return Event(
            source="commodity_prices",
            domain="economics",
            event_type="commodity_price",
            severity=severity,
            geometry={"type": "Point", "coordinates": [0, 0]},
            properties={
                "symbol": symbol,
                "name": commodity.get("name"),
                "price": price,
                "change": change,
                "change_percent": change_pct,
                "unit": commodity.get("unit"),
                "currency": commodity.get("currency"),
                "timestamp": commodity.get("timestamp"),
                "previous_close": commodity.get("previous_close"),
                "open": commodity.get("open"),
                "high": commodity.get("high"),
                "low": commodity.get("low"),
                "volume": commodity.get("volume"),
            },
            metadata={
                "severity_tier": "moderate" if severity >= 0.3 else "low" if severity >= 0.1 else "info",
            },
            timestamp=commodity.get("timestamp", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("commodity_normalize_failed", error=str(e))
        return None