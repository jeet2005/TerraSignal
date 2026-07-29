import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger
from app.core.config import settings


ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"


async def fetch_alpha_vantage(
    function: str,
    symbol: str = None,
    **params
) -> Optional[Dict]:
    url = ALPHA_VANTAGE_BASE_URL
    all_params = {
        "function": function,
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
    }
    if symbol:
        all_params["symbol"] = symbol
    all_params.update(params)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=all_params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("alpha_vantage_fetch_failed", error=str(e), function=function)
            return None


async def fetch_stock_quote(symbol: str) -> Optional[Dict]:
    return await fetch_alpha_vantage("GLOBAL_QUOTE", symbol=symbol)


async def fetch_currency_exchange(from_currency: str, to_currency: str) -> Optional[Dict]:
    return await fetch_alpha_vantage(
        "CURRENCY_EXCHANGE_RATE",
        from_currency=from_currency,
        to_currency=to_currency,
    )


async def fetch_crypto_rating(symbol: str) -> Optional[Dict]:
    return await fetch_alpha_vantage("CRYPTO_RATING", symbol=symbol)


async def fetch_commodity_price(symbol: str) -> Optional[Dict]:
    return await fetch_alpha_vantage("COMMODITY_PRICE", symbol=symbol)


def normalize_stock_quote(data: Dict, symbol: str) -> Optional[Event]:
    try:
        quote = data.get("Global Quote", {})
        if not quote:
            return None
        
        change_pct = quote.get("10. change percent", "0%").replace("%", "")
        severity = min(abs(float(change_pct)) / 100, 1.0) * 0.5
        
        return Event(
            source="alpha_vantage",
            domain="economics",
            event_type="stock_quote",
            severity=severity,
            geometry={"type": "Point", "coordinates": [-74.0060, 40.7128]},  # NYC
            properties={
                "symbol": symbol,
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": change_pct,
                "volume": int(quote.get("06. volume", 0)),
                "latest_trading_day": quote.get("07. latest trading day"),
            },
            metadata={
                "severity_tier": "high" if severity >= 0.4 else "moderate" if severity >= 0.2 else "low" if severity >= 0.1 else "info",
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("alpha_vantage_stock_normalize_failed", error=str(e))
        return None


def normalize_currency_exchange(data: Dict) -> Optional[Event]:
    try:
        rate_data = data.get("Realtime Currency Exchange Rate", {})
        if not rate_data:
            return None
        
        return Event(
            source="alpha_vantage",
            domain="economics",
            event_type="currency_exchange",
            severity=0.1,
            geometry={"type": "Point", "coordinates": [0, 0]},
            properties={
                "from_currency": rate_data.get("1. From_Currency Code"),
                "to_currency": rate_data.get("3. To_Currency Code"),
                "exchange_rate": float(rate_data.get("5. Exchange Rate", 0)),
                "bid_price": float(rate_data.get("8. Bid Price", 0)),
                "ask_price": float(rate_data.get("9. Ask Price", 0)),
                "last_refreshed": rate_data.get("6. Last Refreshed"),
            },
            metadata={"severity_tier": "info"},
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("alpha_vantage_currency_normalize_failed", error=str(e))
        return None