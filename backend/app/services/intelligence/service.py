from datetime import datetime, timedelta
from typing: List, Dict, Any, Optional
from app.models.event import Event
from app.models.compound_event import CompoundEvent
from app.services.intelligence.anomaly_detection import anomaly_detector, baseline_manager, StatisticalAnomalyDetector, RollingBaselineManager
from app.services.intelligence.correlation import correlator, amplifier, CompoundEventCorrelator, SpatialTemporalClusterer, SeverityAmplifier
from app.core.logging import logger


class IntelligenceService:
    """Orchestrates intelligence layer: anomaly detection, correlation, severity amplification"""
    
    def __init__(self):
        self.anomaly_detector = anomaly_detector
        self.baseline_manager = baseline_manager
        self.correlator = correlator
        self.amplifier = amplifier
        
        self.correlation_interval_hours = 1
        self.anomaly_check_interval_minutes = 15
    
    async def run_intelligence_pipeline(
        self,
        events: List[Event],
        min_severity: float = 0.3
    ) -> Dict[str, Any]:
        """Run full intelligence pipeline on events"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "input_events": len(events),
            "anomalies": [],
            "compound_events": [],
            "amplified_events": [],
            "stats": {}
        }
        
        # 1. Anomaly detection
        anomaly_results = await self._detect_anomalies(events)
        results["anomalies"] = anomaly_results
        results["stats"]["anomalies_found"] = len(anomaly_results)
        
        # 2. Spatial-temporal correlation
        correlation_result = await self.correlator.correlate(events, min_severity)
        results["compound_events"] = [
            {
                "id": str(ce.id),
                "title": ce.title,
                "severity": ce.severity,
                "domains": ce.domains,
                "event_count": ce.event_count,
                "radius_km": ce.radius_km,
                "time_span_hours": ce.time_span_hours,
            }
            for ce in correlation_result.compound_events
        ]
        results["stats"]["compound_events_created"] = len(correlation_result.compound_events)
        results["stats"]["clustered_events"] = correlation_result.clustered_events
        
        # 3. Severity amplification for compound events
        for ce in correlation_result.compound_events:
            amplified = self.amplifier.amplify(
                base_severity=ce.severity,
                domains=ce.domains,
                event_count=ce.event_count,
                time_span_hours=ce.time_span_hours,
            )
            if amplified != ce.severity:
                results["amplified_events"].append({
                    "compound_event_id": str(ce.id),
                    "original_severity": ce.severity,
                    "amplified_severity": amplified,
                    "tier": self.amplifier.get_severity_tier(amplified),
                })
                ce.severity = amplified
                await ce.save()
        
        results["stats"]["amplified_count"] = len(results["amplified_events"])
        
        logger.info("intelligence_pipeline_completed", **results["stats"])
        return results
    
    async def _detect_anomalies(self, events: List[Event]) -> List[Dict[str, Any]]:
        """Run statistical anomaly detection on events"""
        anomalies = []
        
        # Group by domain+event_type for baseline comparison
        grouped = {}
        for event in events:
            key = f"{event.domain}:{event.event_type}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(event)
        
        for key, group_events in grouped.items():
            if len(group_events) < 5:
                continue
            
            domain, event_type = key.split(":", 1)
            
            # Check each event for anomalies
            for event in group_events:
                # Extract numeric features for anomaly detection
                features = self._extract_features(event)
                
                result = self.anomaly_detector.detect(
                    features,
                    domain,
                    event_type,
                    region=event.properties.get("country"),
                )
                
                if result["is_anomaly"]:
                    anomalies.append({
                        "event_id": str(event.id),
                        "domain": domain,
                        "event_type": event_type,
                        "anomaly_score": result["anomaly_score"],
                        "anomalous_features": result["anomalous_features"],
                        "severity": event.severity,
                    })
        
        return anomalies
    
    def _extract_features(self, event: Event) -> Dict[str, float]:
        """Extract numeric features from event for anomaly detection"""
        features = {"severity": event.severity}
        
        props = event.properties or {}
        
        # Common numeric properties
        numeric_props = [
            "magnitude", "depth", "temperature", "wind_speed", "humidity",
            "aqi", "brightness", "frp", "altitude", "velocity",
            "price", "market_cap", "volume", "change_percent",
            "goldstein_scale", "avg_tone", "num_mentions", "num_sources",
            "fatalities", "kp_index", "flux",
        ]
        
        for prop in numeric_props:
            if prop in props and props[prop] is not None:
                try:
                    features[prop] = float(props[prop])
                except (ValueError, TypeError):
                    pass
        
        return features
    
    async def update_baselines(self, events: List[Event]):
        """Update rolling baselines with recent events"""
        # Group by domain:event_type
        grouped = {}
        for event in events:
            key = f"{event.domain}:{event.event_type}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(event)
        
        for key, group_events in grouped.items():
            if len(group_events) < 10:
                continue
            
            domain, event_type = key.split(":", 1)
            
            # Extract feature vectors
            feature_vectors = []
            for event in group_events:
                features = self._extract_features(event)
                if len(features) > 1:
                    feature_vectors.append(list(features.values()))
            
            if feature_vectors:
                self.baseline_manager.update(key, feature_vectors)
        
        logger.info("baselines_updated", domains=list(grouped.keys()))
    
    async def get_intelligence_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get intelligence summary for dashboard"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Get compound events
        compounds = await CompoundEvent.find(
            CompoundEvent.start_time >= since.isoformat()
        ).sort(-CompoundEvent.severity).to_list()
        
        # Get anomalies (would need to be stored)
        # For now return compound stats
        
        summary = {
            "period_hours": hours,
            "compound_events": len(compounds),
            "critical_compounds": len([c for c in compounds if c.severity >= 0.8]),
            "high_compounds": len([c for c in compounds if 0.6 <= c.severity < 0.8]),
            "top_domains": self._get_top_domains(compounds),
            "avg_event_count": sum(c.event_count for c in compounds) / len(compounds) if compounds else 0,
            "max_radius_km": max((c.radius_km for c in compounds), default=0),
            "max_time_span_hours": max((c.time_span_hours for c in compounds), default=0),
        }
        
        return summary
    
    def _get_top_domains(self, compounds: List[CompoundEvent]) -> List[Dict[str, Any]]:
        domain_counts = {}
        for c in compounds:
            for d in c.domains:
                domain_counts[d] = domain_counts.get(d, 0) + 1
        
        sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"domain": d, "count": c} for d, c in sorted_domains[:10]]


intelligence_service = IntelligenceService()