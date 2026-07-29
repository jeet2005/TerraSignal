import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


WORLD_BANK_BASE_URL = "https://api.worldbank.org/v2"


async def fetch_world_bank_indicators(
    indicator: str,
    country: str = "all",
    date: str = "2020:2023",
    per_page: int = 100
) -> List[Dict]:
    url = f"{WORLD_BANK_BASE_URL}/country/{country}/indicator/{indicator}"
    params = {
        "format": "json",
        "date": date,
        "per_page": per_page,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if len(data) > 1:
                return data[1]
            return []
        except Exception as e:
            logger.error("world_bank_fetch_failed", error=str(e), indicator=indicator)
            return []


async def fetch_world_bank_countries() -> List[Dict]:
    url = f"{WORLD_BANK_BASE_URL}/country"
    params = {"format": "json", "per_page": 300}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if len(data) > 1:
                return data[1]
            return []
        except Exception as e:
            logger.error("world_bank_countries_fetch_failed", error=str(e))
            return []


WORLD_BANK_KEY_INDICATORS = {
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
    "SP.POP.TOTL": "Population, total",
    "SP.DYN.LE00.IN": "Life expectancy at birth",
    "SL.UEM.TOTL.ZS": "Unemployment, total (% of labor force)",
    "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
    "NE.TRD.GNFS.ZS": "Trade (% of GDP)",
    "BN.CAB.XOKA.CD": "Current account balance",
    "DT.DOD.DECT.EX.ZS": "External debt stocks (% of GNI)",
    "EG.ELC.ACCS.ZS": "Access to electricity (% of population)",
    "EN.ATM.CO2E.PC": "CO2 emissions (metric tons per capita)",
    "SE.XPD.TOTL.GD.ZS": "Government expenditure on education (% of GDP)",
    "SH.XPD.CHEX.GD.ZS": "Current health expenditure (% of GDP)",
}


def normalize_world_bank_data(data: List[Dict], indicator_code: str, indicator_name: str) -> List[Event]:
    events = []
    for item in data:
        try:
            country = item.get("country", {})
            country_name = country.get("value", "")
            country_code = country.get("id", "")
            value = item.get("value")
            year = item.get("date")
            
            if value is None:
                continue
            
            events.append(Event(
                source="world_bank",
                domain="economics",
                event_type="development_indicator",
                severity=0.1,
                geometry={"type": "Point", "coordinates": [0, 0]},
                properties={
                    "indicator_code": indicator_code,
                    "indicator_name": indicator_name,
                    "country": country_name,
                    "country_code": country_code,
                    "value": value,
                    "year": year,
                    "unit": item.get("unit", ""),
                },
                metadata={"severity_tier": "info"},
                timestamp=f"{year}-01-01T00:00:00" if year else datetime.utcnow().isoformat(),
            ))
        except Exception as e:
            logger.error("world_bank_normalize_failed", error=str(e))
    return events