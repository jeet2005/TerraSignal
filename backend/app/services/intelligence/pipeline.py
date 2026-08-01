from datetime import datetime, timedelta
from typing: List, Dict, Any, Optional
from app.models.event import Event, CompoundEvent
from app.services.intelligence.anomaly_detection import anomaly_detector, baseline_manager
from app.services.intelligence.correlation import clusterer, correlator, amplifier
from app.core.logging import logger


async def run_intelligence_pipeline(hours: int = 6) -> Dict[str, Any]:
    """Run the full intelligence pipeline on recent events"""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    events = await Event.find({
        "timestamp": {"$gte": cutoff.isoformat()},
    }).to_list()
    
    if not events:
        return {"events_processed": 0, "compound_events_created": 0, "anomalies_detected": 0}
    
    logger.info("intelligence_pipeline_started", events_count=len(events))
    
    # Update baselines
    await baseline_manager.scheduled_update()
    
    # Detect anomalies
    anomalies = []
    for event in events:
        features = {"severity": event.severity}
        props = event.properties or {}
        for k, v in props.items():
            if isinstance(v, (int, float)):
                features[k] = float(v)
        
        result = anomaly_detector.detect(
            features=features,
            domain=event.domain,
            event_type=event.event_type,
        )
        
        if result["is_anomaly"]:
            anomalies.append({
                "event_id": str(event.id),
                "event": event,
                "result": result,
            })
    
    logger.info("anomaly_detection_completed", anomalies_count=len(anomalies))
    
    # Spatial-temporal clustering
    clusters = await clusterer.cluster_events(events)
    
    logger.info("clustering_completed", clusters_count=len(clusters))
    
    # Compound event correlation
    correlation_results = await correlator.find_compound_events(clusters)
    
    compound_created = 0
    for result in correlation_results:
        if result.compound_event:
            compound_created += 1
    
    logger.info("correlation_completed", compound_events_created=compound_created)
    
    return {
        "events_processed": len(events),
        "time_range_hours": hours,
        "anomalies_detected": len(anomalies),
        "clusters_found": len(clusters),
        "compound_events_created": compound_created,
        "anomalies": anomalies,
        "clusters": clusters,
        "correlations": correlation_results,
    }


async def run_scheduled_intelligence():
    """Scheduled intelligence pipeline run"""
    logger.info("scheduled_intelligence_pipeline_started")
    
    result = await run_intelligence_pipeline(hours=6)
    
    logger.info("scheduled_intelligence_pipeline_completed", **result)
    return result


async def get_domain_intelligence(domain: str, hours: int = 24) -> Dict[str, Any]:
    """Get intelligence summary for a specific domain"""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    events = await Event.find({
        "domain": domain,
        "timestamp": {"$gte": cutoff.isoformat()},
    }).to_list()
    
    compound_events = await CompoundEvent.find({
        "domains": domain,
        "detected_at": {"$gte": cutoff.isoformat()},
    }).to_list()
    
    # Anomaly stats
    anomaly_result = anomaly_detector.detect(
        features={"severity": sum(e.severity for e in events) / len(events) if events else 0},
        domain=domain,
        event_type="all",
    )
    
    return {
        "domain": domain,
        "time_range_hours": hours,
        "event_count": len(events),
        "compound_event_count": len(compound_events),
        "avg_severity": sum(e.severity for e in events) / len(events) if events else 0,
        "max_severity": max((e.severity for e in events), default=0),
        "domains_in_compounds": list(set(d for c in compound_events for d in c.domains)),
        "top_event_types": _get_top_event_types(events),
        "severity_distribution": _get_severity_distribution(events),
        "recent_anomalies": anomaly_result.get("anomalous_features", []),
    }


def _get_top_event_types(events: List[Event], top_n: int = 10) -> List[Dict[str, Any]]:
    counts = {}
    for e in events:
        key = f"{e.domain}:{e.event_type}"
        counts[key] = counts.get(key, 0) + 1
    
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"event_type": k, "count": v} for k, v in sorted_counts[:top_n]]


def _get_severity_distribution(events: List[Event]) -> Dict[str, int]:
    tiers = {"critical": 0, "high": 0, "moderate": 0, "low": 0, "info": 0}
    for e in events:
        if e.severity >= 0.8:
            tiers["critical"] += 1
        elif e.severity >= 0.6:
            tiers["high"] += 1
        elif e.severity >= 0.4:
            tiers["moderate"] += 1
        elif e.severity >= 0.2:
            tiers["low"] += 1
        else:
            tiers["info"] += 1
    return tiers