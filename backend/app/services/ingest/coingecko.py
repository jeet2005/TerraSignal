import httpx
from datetime import datetime
from typing import List, Dict, Optional
from app.models.event import Event
from app.core.logging import logger
from app.core.config import settings


COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


def calculate_severity(domain: str, **kwargs) -> float:
    if domain == "crypto":
        market_cap = kwargs.get("market_cap", 0)
        change_24h = kwargs.get("price_change_24h", 0)
        if market_cap > 100_000_000_000:
            base = 0.3
        elif market_cap > 10_000_000_000:
            base = 0.2
        elif market_cap > 1_000_000_000:
            base = 0.15
        else:
            base = 0.1
        
        volatility = min(abs(change_24h) / 100, 0.3)
        return min(base + volatility, 0.6)
    return 0.1


async def fetch_coingecko_markets(vs_currency: str = "usd") -> List[Dict]:
    url = f"{COINGECKO_BASE_URL}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "price_change_percentage": "24h,7d",
    }
    
    headers = {}
    if settings.COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = settings.COINGECKO_API_KEY
    
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("coingecko_fetch_failed", error=str(e))
            return []


async def fetch_coingecko_global() -> Dict:
    url = f"{COINGECKO_BASE_URL}/global"
    
    headers = {}
    if settings.COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = settings.COINGECKO_API_KEY
    
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json().get("data", {})
        except Exception as e:
            logger.error("coingecko_global_fetch_failed", error=str(e))
            return {}


async def fetch_coingecko_trending() -> List[Dict]:
    url = f"{COINGECKO_BASE_URL}/search/trending"
    
    headers = {}
    if settings.COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = settings.COINGECKO_API_KEY
    
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json().get("coins", [])
        except Exception as e:
            logger.error("coingecko_trending_fetch_failed", error=str(e))
            return []


def normalize_coingecko_coin(coin: Dict) -> Optional[Event]:
    try:
        market_cap = coin.get("market_cap", 0)
        change_24h = coin.get("price_change_percentage_24h", 0)
        severity = calculate_severity("crypto", market_cap=market_cap, price_change_24h=change_24h)
        
        return Event(
            source="coingecko",
            domain="crypto",
            event_type="market_data",
            severity=severity,
            geometry={"type": "Point", "coordinates": [0, 0]},
            properties={
                "id": coin.get("id"),
                "symbol": coin.get("symbol", "").upper(),
                "name": coin.get("name"),
                "current_price": coin.get("current_price"),
                "market_cap": market_cap,
                "market_cap_rank": coin.get("market_cap_rank"),
                "volume_24h": coin.get("total_volume"),
                "price_change_24h": coin.get("price_change_24h"),
                "price_change_percentage_24h": change_24h,
                "price_change_percentage_7d": coin.get("price_change_percentage_7d"),
                "circulating_supply": coin.get("circulating_supply"),
                "total_supply": coin.get("total_supply"),
                "max_supply": coin.get("max_supply"),
                "ath": coin.get("ath"),
                "ath_change_percentage": coin.get("ath_change_percentage"),
                "atl": coin.get("atl"),
                "atl_change_percentage": coin.get("atl_change_percentage"),
            },
            metadata={
                "severity_tier": "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("coingecko_normalize_failed", error=str(e))
        return None


async def fetch_coingecko_all() -> Dict:
    markets = await fetch_coingecko_markets()
    global_data = await fetch_coingecko_global()
    trending = await fetch_coingecko_trending()
    return {"markets": markets, "global": global_data, "trending": trending}