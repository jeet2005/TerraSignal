from datetime import datetime, timedelta
from typing: List, Dict, Any, Optional
from dataclasses import dataclass
import math
from app.models.event import Event
from app.core.logging import logger


@dataclass
class BaselineStats:
    mean: float
    std_dev: float
    count: int
    min_val: float
    max_val: float
    percentile_95: float
    percentile_99: float
    feature_name: str
    domain: str
    event_type: str
    updated_at: datetime


class StatisticalAnomalyDetector:
    """Z-score based anomaly detection with 7-day rolling baselines"""
    
    def __init__(self, window_days: int = 7, z_threshold: float = 2.0):
        self.window_days = window_days
        self.z_threshold = z_threshold
        self.baselines: Dict[str, Dict[str, BaselineStats]] = {}
    
    def _get_key(self, domain: str, event_type: str, feature: str) -> str:
        return f"{domain}:{event_type}:{feature}"
    
    async def compute_baseline(
        self,
        domain: str,
        event_type: str,
        feature: str,
        region: Optional[str] = None
    ) -> BaselineStats:
        """Compute 7-day rolling baseline for a feature"""
        cutoff = datetime.utcnow() - timedelta(days=self.window_days)
        
        query = {
            "domain": domain,
            "event_type": event_type,
            "timestamp": {"$gte": cutoff.isoformat()},
        }
        
        if region:
            query["properties.region"] = region
        
        events = await Event.find(query).to_list()
        
        if not events:
            return BaselineStats(0, 0, 0, 0, 0, 0, 0, feature, domain, event_type, datetime.utcnow())
        
        values = []
        for e in events:
            val = self._extract_feature(e, feature)
            if val is not None:
                values.append(val)
        
        if len(values) < 3:
            return BaselineStats(0, 0, len(values), 0, 0, 0, 0, feature, domain, event_type, datetime.utcnow())
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance) if variance > 0 else 0
        
        sorted_values = sorted(values)
        p95_idx = int(len(sorted_values) * 0.95)
        p99_idx = int(len(sorted_values) * 0.99)
        
        return BaselineStats(
            mean=mean,
            std_dev=std_dev,
            count=len(values),
            min_val=min(values),
            max_val=max(values),
            percentile_95=sorted_values[min(p95_idx, len(sorted_values) - 1)],
            percentile_99=sorted_values[min(p99_idx, len(sorted_values) - 1)],
            feature_name=feature,
            domain=domain,
            event_type=event_type,
            updated_at=datetime.utcnow(),
        )
    
    def _extract_feature(self, event: Event, feature: str) -> Optional[float]:
        """Extract feature value from event"""
        if feature == "severity":
            return event.severity
        
        props = event.properties or {}
        if feature in props and props[feature] is not None:
            try:
                return float(props[feature])
            except (ValueError, TypeError):
                return None
        
        return None
    
    def calculate_z_score(self, value: float, baseline: BaselineStats) -> float:
        if baseline.std_dev == 0:
            return 0.0
        return (value - baseline.mean) / baseline.std_dev
    
    def detect(
        self,
        features: Dict[str, float],
        domain: str,
        event_type: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Detect anomalies in features"""
        anomalous_features = []
        max_z_score = 0
        
        for feature_name, value in features.items():
            key = self._get_key(domain, event_type, feature_name)
            
            if key not in self.baselines:
                baseline = BaselineStats(
                    mean=value,
                    std_dev=0,
                    count=1,
                    min_val=value,
                    max_val=value,
                    percentile_95=value,
                    percentile_99=value,
                    feature_name=feature_name,
                    domain=domain,
                    event_type=event_type,
                    updated_at=datetime.utcnow(),
                )
                if domain not in self.baselines:
                    self.baselines[domain] = {}
                self.baselines[domain][f"{event_type}:{feature_name}"] = baseline
                continue
            
            baseline = self.baselines[domain][f"{event_type}:{feature_name}"]
            z_score = self.calculate_z_score(value, baseline)
            
            if abs(z_score) > max_z_score:
                max_z_score = abs(z_score)
            
            if abs(z_score) > self.z_threshold:
                anomalous_features.append({
                    "feature": feature_name,
                    "value": value,
                    "baseline_mean": baseline.mean,
                    "baseline_std": baseline.std_dev,
                    "z_score": z_score,
                    "direction": "positive" if z_score > 0 else "negative",
                })
        
        is_anomaly = len(anomalous_features) > 0
        anomaly_score = min(max_z_score / 5.0, 1.0) if max_z_score > 0 else 0.0
        
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": anomaly_score,
            "max_z_score": max_z_score,
            "anomalous_features": anomalous_features,
        }
    
    async def update_all_baselines(self, events: List[Event]):
        """Update baselines from recent events"""
        domain_event_types = {}
        for e in events:
            key = f"{e.domain}:{e.event_type}"
            if key not in domain_event_types:
                domain_event_types[key] = []
            domain_event_types[key].append(e)
        
        for key, group_events in domain_event_types.items():
            domain, event_type = key.split(":", 1)
            
            features = set()
            for e in group_events:
                props = e.properties or {}
                features.add("severity")
                for k, v in props.items():
                    if isinstance(v, (int, float)):
                        features.add(k)
            
            for feature in features:
                baseline = await self.compute_baseline(domain, event_type, feature)
                if baseline.count >= 10:
                    if domain not in self.baselines:
                        self.baselines[domain] = {}
                    self.baselines[domain][f"{event_type}:{feature}"] = baseline
        
        logger.info("baselines_updated", domains=list(self.baselines.keys()))


class RollingBaselineManager:
    """Manages 7-day rolling baselines for all domain/event_type combinations"""
    
    def __init__(self, detector: StatisticalAnomalyDetector):
        self.detector = detector
        self.last_full_update: Optional[datetime] = None
        self.update_interval_hours = 1
    
    async def scheduled_update(self):
        """Run scheduled baseline update"""
        now = datetime.utcnow()
        if (self.last_full_update and 
            (now - self.last_full_update).total_seconds() < self.update_interval_hours * 3600):
            return
        
        cutoff = now - timedelta(days=self.detector.window_days)
        events = await Event.find({"timestamp": {"$gte": cutoff.isoformat()}}).to_list()
        
        await self.detector.update_all_baselines(events)
        self.last_full_update = now
        
        logger.info("scheduled_baseline_update_completed")


anomaly_detector = StatisticalAnomalyDetector()
baseline_manager = RollingBaselineManager(anomaly_detector)