import httpx
import json
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger


WIKIMEDIA_EVENTSTREAM_URL = "https://stream.wikimedia.org/v2/stream/recentchange"


async def fetch_wikimedia_events(limit: int = 100) -> List[Dict]:
    events = []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("GET", WIKIMEDIA_EVENTSTREAM_URL) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip():
                            try:
                                event = json.loads(data)
                                events.append(event)
                                if len(events) >= limit:
                                    break
                            except json.JSONDecodeError:
                                continue
    except Exception as e:
        logger.error("wikimedia_fetch_failed", error=str(e))
    return events


def normalize_wikimedia_event(event: Dict) -> Optional[Event]:
    try:
        meta = event.get("meta", {})
        page = event.get("page", {})
        performer = event.get("performer", {})
        
        domain = meta.get("domain", "")
        wiki = domain.replace(".wikipedia.org", "").replace(".wikimedia.org", "")
        
        severity = 0.05
        if event.get("type") == "new":
            severity = 0.15
        elif event.get("bot", False):
            severity = 0.02
        elif event.get("minor", False):
            severity = 0.03
        
        return Event(
            source="wikimedia",
            domain="digital",
            event_type="wiki_edit",
            severity=severity,
            geometry={"type": "Point", "coordinates": [0, 0]},
            properties={
                "id": event.get("id"),
                "type": event.get("type"),
                "namespace": page.get("namespace"),
                "title": page.get("title"),
                "page_id": page.get("page_id"),
                "comment": event.get("comment"),
                "timestamp": event.get("timestamp"),
                "user": performer.get("user_text"),
                "user_id": performer.get("user_id"),
                "bot": performer.get("bot", False),
                "minor": event.get("minor", False),
                "flags": event.get("flags", []),
                "wiki": wiki,
                "domain": domain,
                "length_old": event.get("length", {}).get("old"),
                "length_new": event.get("length", {}).get("new"),
            },
            metadata={"severity_tier": "info"},
            timestamp=event.get("timestamp", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("wikimedia_normalize_failed", error=str(e))
        return None