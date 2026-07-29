import httpx
from datetime import datetime
from typing import Optional, List, Dict
from app.models.event import Event
from app.core.logging import logger
from app.core.config import settings


TOMTOM_BASE_URL = "https://api.tomtom.com/traffic/services/4"


async def fetch_tomtom_incidents(
    bbox: str = "-180,-90,180,90",
    fields: str = "{incidents{type,geometry{type,coordinates},properties{iconCategory,description,startTime,endTime,from,to,length,delay,roadNumbers}}}"
) -> List[Dict]:
    url = f"{TOMTOM_BASE_URL}/incidentDetails/3/json"
    params = {
        "key": settings.TOMTOM_API_KEY,
        "bbox": bbox,
        "fields": fields,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("incidents", [])
        except Exception as e:
            logger.error("tomtom_incidents_fetch_failed", error=str(e))
            return []


async def fetch_tomtom_flow(
    bbox: str = "-180,-90,180,90",
    zoom: int = 10
) -> List[Dict]:
    url = f"{TOMTOM_BASE_URL}/flowSegmentData/absolute/{zoom}/json"
    params = {
        "key": settings.TOMTOM_API_KEY,
        "bbox": bbox,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return [data.get("flowSegmentData", {})]
        except Exception as e:
            logger.error("tomtom_flow_fetch_failed", error=str(e))
            return []


def calculate_traffic_severity(delay: float, length: float) -> float:
    if delay >= 600:
        return 0.7
    elif delay >= 300:
        return 0.5
    elif delay >= 60:
        return 0.3
    else:
        return 0.1


def normalize_tomtom_incident(incident: Dict) -> Optional[Event]:
    try:
        props = incident.get("properties", {})
        geom = incident.get("geometry", {})
        coords = geom.get("coordinates", [0, 0])
        
        delay = props.get("delay", 0)
        length = props.get("length", 0)
        severity = calculate_traffic_severity(delay, length)
        
        return Event(
            source="tomtom",
            domain="traffic",
            event_type="incident",
            severity=severity,
            geometry={"type": "Point", "coordinates": coords},
            properties={
                "type": incident.get("type"),
                "icon_category": props.get("iconCategory"),
                "description": props.get("description"),
                "start_time": props.get("startTime"),
                "end_time": props.get("endTime"),
                "from_location": props.get("from"),
                "to_location": props.get("to"),
                "length": length,
                "delay": delay,
                "road_numbers": props.get("roadNumbers"),
            },
            metadata={
                "severity_tier": "high" if severity >= 0.6 else "moderate" if severity >= 0.4 else "low" if severity >= 0.2 else "info",
            },
            timestamp=props.get("startTime", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error("tomtom_incident_normalize_failed", error=str(e))
        return None


def normalize_tomtom_flow(flow: Dict) -> Optional[Event]:
    try:
        coords = flow.get("coordinates", {})
        lon = coords.get("longitude", 0)
        lat = coords.get("latitude", 0)
        
        current_speed = flow.get("currentSpeed", 0)
        free_flow_speed = flow.get("freeFlowSpeed", 1)
        congestion = 1 - (current_speed / free_flow_speed) if free_flow_speed > 0 else 0
        severity = min(congestion * 0.5, 0.5)
        
        return Event(
            source="tomtom",
            domain="traffic",
            event_type="flow",
            severity=severity,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            properties={
                "current_speed": current_speed,
                "free_flow_speed": free_flow_speed,
                "congestion": congestion,
                "confidence": flow.get("confidence"),
                "road_closure": flow.get("roadClosure"),
            },
            metadata={"severity_tier": "info"},
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("tomtom_flow_normalize_failed", error=str(e))
        return None