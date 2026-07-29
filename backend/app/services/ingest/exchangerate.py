import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger
from app.core.config import settings


EXCHANGE_RATE_BASE_URL = "https://api.exchangerate-api.com/v4"


async def fetch_exchange_rates(base: str = "USD") -> Optional[Dict]:
    url = f"{EXCHANGE_RATE_BASE_URL}/latest/{base}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("exchangerate_fetch_failed", error=str(e))
            return None


async def fetch_exchange_rate_history(base: str, start_date: str, end_date: str) -> Optional[Dict]:
    url = f"{EXCHANGE_RATE_BASE_URL}/history"
    params = {
        "base": base,
        "start_at": start_date,
        "end_at": end_date,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("exchangerate_history_fetch_failed", error=str(e))
            return None


def normalize_exchange_rates(data: Dict) -> Optional[Event]:
    try:
        base = data.get("base", "USD")
        rates = data.get("rates", {})
        date = data.get("date")
        
        return Event(
            source="exchangerate_api",
            domain="economics",
            event_type="currency_rates",
            severity=0.1,
            geometry={"type": "Point", "coordinates": [0, 0]},
            properties={
                "base_currency": base,
                "date": date,
                "rates": rates,
                "rate_count": len(rates),
            },
            metadata={"severity_tier": "info"},
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("exchangerate_normalize_failed", error=str(e))
        return None