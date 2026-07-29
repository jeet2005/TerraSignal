import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


GDELT_DOC_BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


async def fetch_gdelt_doc(
    query: str = "",
    mode: str = "artlist",
    format: str = "json",
    max_records: int = 250,
    timespan: str = "24h",
    domain: str = None,
    country: str = None,
    lang: str = None,
) -> List[Dict]:
    params = {
        "query": query,
        "mode": mode,
        "format": format,
        "maxrecords": max_records,
        "timespan": timespan,
    }
    
    if domain:
        params["domain"] = domain
    if country:
        params["country"] = country
    if lang:
        params["lang"] = lang
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.get(GDELT_DOC_BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("articles", [])
        except Exception as e:
            logger.error("gdelt_doc_fetch_failed", error=str(e))
            return []


def normalize_gdelt_doc(article: Dict) -> Optional[Event]:
    try:
        lat = article.get("location", {}).get("latitude")
        lon = article.get("location", {}).get("longitude")
        
        coords = [0, 0]
        if lat is not None and lon is not None:
            coords = [float(lon), float(lat)]
        
        tone = article.get("tone", 0)
        severity = min(abs(tone) * 0.1, 0.5)
        
        return Event(
            source="gdelt_doc",
            domain="geopolitical",
            event_type="news_article",
            severity=severity,
            geometry={"type": "Point", "coordinates": coords},
            properties={
                "url": article.get("url"),
                "title": article.get("title"),
                "seendate": article.get("seendate"),
                "socialimage": article.get("socialimage"),
                "domain": article.get("domain"),
                "language": article.get("lang"),
                "sourcecountry": article.get("sourcecountry"),
                "tone": tone,
                "wordcount": article.get("wordcount"),
                "theme": article.get("theme"),
            },
            metadata={
                "severity_tier": "moderate" if severity >= 0.3 else "low" if severity >= 0.1 else "info",
            },
            timestamp=article.get("seendate", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("gdelt_doc_normalize_failed", error=str(e))
        return None