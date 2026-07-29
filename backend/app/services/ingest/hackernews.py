import httpx
from datetime import datetime
from typing: Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


HACKER_NEWS_BASE_URL = "https://hacker-news.firebaseio.com/v0"


async def fetch_hn_top_stories() -> List[int]:
    url = f"{HACKER_NEWS_BASE_URL}/topstories.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()[:100]
        except Exception as e:
            logger.error("hn_topstories_fetch_failed", error=str(e))
            return []


async def fetch_hn_new_stories() -> List[int]:
    url = f"{HACKER_NEWS_BASE_URL}/newstories.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()[:100]
        except Exception as e:
            logger.error("hn_newstories_fetch_failed", error=str(e))
            return []


async def fetch_hn_item(item_id: int) -> Optional[Dict]:
    url = f"{HACKER_NEWS_BASE_URL}/item/{item_id}.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("hn_item_fetch_failed", error=str(e), item_id=item_id)
            return None


async def fetch_hn_batch(item_ids: List[int]) -> List[Dict]:
    items = []
    for item_id in item_ids[:20]:
        item = await fetch_hn_item(item_id)
        if item:
            items.append(item)
    return items


def normalize_hn_item(item: Dict) -> Optional[Event]:
    try:
        if item.get("type") != "story":
            return None
        
        score = item.get("score", 0)
        descendants = item.get("descendants", 0)
        
        severity = min((score / 1000) * 0.5 + (descendants / 200) * 0.3, 0.5)
        
        return Event(
            source="hacker_news",
            domain="digital",
            event_type="hn_story",
            severity=severity,
            geometry={"type": "Point", "coordinates": [-122.4194, 37.7749]},
            properties={
                "hn_id": item.get("id"),
                "title": item.get("title"),
                "url": item.get("url"),
                "score": score,
                "descendants": descendants,
                "by": item.get("by"),
                "time": item.get("time"),
                "text": item.get("text"),
                "type": item.get("type"),
            },
            metadata={
                "severity_tier": "moderate" if severity >= 0.3 else "low" if severity >= 0.1 else "info",
            },
            timestamp=datetime.fromtimestamp(item.get("time", 0)).isoformat() if item.get("time") else datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("hn_normalize_failed", error=str(e))
        return None