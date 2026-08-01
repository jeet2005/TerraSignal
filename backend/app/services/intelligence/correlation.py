from datetime import datetime, timedelta
from typing: List, Dict, Any, Optional
from dataclasses import dataclass
from app.models.event import Event
from app.models.compound_event import CompoundEvent
from app.core.logging import logger
import math


@dataclass
class EventCluster:
    events: List[Event]
    centroid: Dict[str, Any]
    radius_km: float
    domains: List[str]
    start_time: datetime
    end_time: datetime
    time_span_hours: float
    base_severity: float


@dataclass
class CorrelationResult:
    compound_event: CompoundEvent
    clusters: List[EventCluster]
    amplification_factor: float
    correlations_found: int


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km using Haversine formula"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_centroid(events: List[Event]) -> Dict[str, Any]:
    """Calculate geographic centroid of events"""
    if not events:
        return {"type": "Point", "coordinates": [0, 0]}
    
    lons = []
    lats = []
    for e in events:
        coords = e.geometry.get("coordinates", [0, 0])
        lons.append(coords[0])
        lats.append(coords[1])
    
    return {
        "type": "Point",
        "coordinates": [sum(lons) / len(lons), sum(lats) / len(lats)]
    }


class SpatialTemporalClusterer:
    """DBSCAN-like clustering for spatial-temporal event correlation"""
    
    def __init__(
        self,
        spatial_eps_km: float = 150,
        temporal_eps_hours: float = 6,
        min_samples: int = 2
    ):
        self.spatial_eps = spatial_eps_km
        self.temporal_eps = temporal_eps_hours
        self.min_samples = min_samples
    
    def cluster(self, events: List[Event]) -> List[EventCluster]:
        """Cluster events using spatial-temporal DBSCAN"""
        if len(events) < self.min_samples:
            return []
        
        # Sort by time
        events = sorted(events, key=lambda e: e.timestamp)
        
        clusters = []
        visited = set()
        
        for i, event in enumerate(events):
            if i in visited:
                continue
            
            neighbors = self._get_neighbors(events, i)
            
            if len(neighbors) < self.min_samples:
                continue
            
            # Expand cluster
            cluster_indices = set(neighbors)
            queue = list(neighbors)
            
            while queue:
                idx = queue.pop(0)
                if idx in visited:
                    continue
                visited.add(idx)
                
                new_neighbors = self._get_neighbors(events, idx)
                if len(new_neighbors) >= self.min_samples:
                    for n_idx in new_neighbors:
                        if n_idx not in cluster_indices:
                            cluster_indices.add(n_idx)
                            queue.append(n_idx)
            
            # Create cluster
            cluster_events = [events[idx] for idx in cluster_indices]
            if len(cluster_events) >= self.min_samples:
                cluster = self._create_cluster(cluster_events)
                if cluster:
                    clusters.append(cluster)
        
        return clusters
    
    def _get_neighbors(self, events: List[Event], idx: int) -> List[int]:
        """Find all events within spatial and temporal epsilon"""
        event = events[idx]
        neighbors = []
        
        coords = event.geometry.get("coordinates", [0, 0])
        lon, lat = coords[0], coords[1]
        event_time = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
        
        for j, other in enumerate(events):
            if j == idx:
                continue
            
            other_coords = other.geometry.get("coordinates", [0, 0])
            other_lon, other_lat = other_coords[0], other_coords[1]
            other_time = datetime.fromisoformat(other.timestamp.replace("Z", "+00:00"))
            
            spatial_dist = haversine_distance(lat, lon, other_lat, other_lon)
            temporal_dist = abs((event_time - other_time).total_seconds() / 3600)
            
            if spatial_dist <= self.spatial_eps and temporal_dist <= self.temporal_eps:
                neighbors.append(j)
        
        return neighbors
    
    def _create_cluster(self, events: List[Event]) -> Optional[EventCluster]:
        """Create cluster object from events"""
        if not events:
            return None
        
        centroid = calculate_centroid(events)
        coords = centroid["coordinates"]
        
        # Calculate radius
        max_dist = 0
        for e in events:
            e_coords = e.geometry.get("coordinates", [0, 0])
            dist = haversine_distance(coords[1], coords[0], e_coords[1], e_coords[0])
            max_dist = max(max_dist, dist)
        
        # Time span
        times = [datetime.fromisoformat(e.timestamp.replace("Z", "+00:00")) for e in events]
        start_time = min(times)
        end_time = max(times)
        time_span = (end_time - start_time).total_seconds() / 3600
        
        # Domains
        domains = list(set(e.domain for e in events))
        
        # Base severity (max)
        base_severity = max(e.severity for e in events)
        
        return EventCluster(
            events=events,
            centroid=centroid,
            radius_km=max_dist,
            domains=domains,
            start_time=start_time,
            end_time=end_time,
            time_span_hours=time_span,
            base_severity=base_severity,
        )


class CompoundEventCorrelator:
    """Correlate events into compound events with cross-domain analysis"""
    
    def __init__(
        self,
        spatial_radius_km: float = 150,
        temporal_window_hours: float = 6,
        min_domains: int = 2,
        min_events: int = 3,
    ):
        self.clusterer = SpatialTemporalClusterer(
            spatial_eps_km=spatial_radius_km,
            temporal_eps_hours=temporal_window_hours,
            min_samples=min_events,
        )
        self.min_domains = min_domains
        self.min_events = min_events
    
    async def correlate(self, events: List[Event]) -> List[CorrelationResult]:
        """Find compound events from raw events"""
        # Group by spatial region for efficiency
        spatial_groups = self._spatial_partition(events)
        
        results = []
        
        for group in spatial_groups:
            if len(group) < self.min_events:
                continue
            
            clusters = self.clusterer.cluster(group)
            
            for cluster in clusters:
                if len(cluster.domains) < self.min_domains:
                    continue
                
                result = await self._create_compound_event(cluster)
                if result:
                    results.append(result)
        
        return results
    
    def _spatial_partition(self, events: List[Event], grid_size_km: float = 300) -> List[List[Event]]:
        """Partition events into spatial grid cells"""
        cells = {}
        
        for event in events:
            coords = event.geometry.get("coordinates", [0, 0])
            lon, lat = coords[0], coords[1]
            
            # Simple grid hashing
            cell_x = int(lon / (grid_size_km / 111))
            cell_y = int(lat / (grid_size_km / 111))
            cell_key = f"{cell_x}:{cell_y}"
            
            if cell_key not in cells:
                cells[cell_key] = []
            cells[cell_key].append(event)
        
        return list(cells.values())
    
    async def _create_compound_event(self, cluster: EventCluster) -> Optional[CorrelationResult]:
        """Create compound event from cluster"""
        try:
            # Calculate amplification
            amplifier = SeverityAmplifier()
            amplification = amplifier.calculate_amplification(
                domains=cluster.domains,
                event_count=len(cluster.events),
                time_span_hours=cluster.time_span_hours,
                radius_km=cluster.radius_km,
            )
            
            compound_severity = min(cluster.base_severity * amplification, 1.0)
            severity_tier = self._get_severity_tier(compound_severity)
            
            # Create compound event
            compound = CompoundEvent(
                start_time=cluster.start_time,
                end_time=cluster.end_time,
                detected_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24),
                centroid=cluster.centroid,
                radius_km=cluster.radius_km,
                domains=cluster.domains,
                event_ids=[str(e.id) for e in cluster.events],
                event_count=len(cluster.events),
                time_span_hours=cluster.time_span_hours,
                severity=compound_severity,
                severity_tier=severity_tier,
                amplification_factor=amplification,
                status="active",
            )
            
            await compound.insert()
            
            return CorrelationResult(
                compound_event=compound,
                clusters=[cluster],
                amplification_factor=amplification,
                correlations_found=len(cluster.events),
            )
            
        except Exception as e:
            logger.error("compound_event_creation_failed", error=str(e))
            return None
    
    def _get_severity_tier(self, severity: float) -> str:
        if severity >= 0.8:
            return "critical"
        elif severity >= 0.6:
            return "high"
        elif severity >= 0.4:
            return "moderate"
        elif severity >= 0.2:
            return "low"
        return "info"


class SeverityAmplifier:
    """Calculate severity amplification for compound events"""
    
    # Domain combination multipliers
    DOMAIN_MULTIPLIERS = {
        frozenset(["seismic", "fire"]): 1.5,
        frozenset(["seismic", "storm"]): 1.3,
        frozenset(["fire", "storm"]): 1.4,
        frozenset(["disaster", "humanitarian"]): 1.6,
        frozenset(["conflict", "humanitarian"]): 1.7,
        frozenset(["space_weather", "aviation"]): 1.3,
        frozenset(["space_weather", "maritime"]): 1.2,
        frozenset(["economics", "geopolitical"]): 1.4,
        frozenset(["crypto", "economics"]): 1.2,
        frozenset(["digital", "geopolitical"]): 1.3,
    }
    
    # Domain severity weights
    DOMAIN_WEIGHTS = {
        "seismic": 1.0,
        "fire": 0.9,
        "storm": 0.8,
        "disaster": 1.0,
        "humanitarian": 0.9,
        "conflict": 1.0,
        "space_weather": 0.7,
        "aviation": 0.3,
        "maritime": 0.3,
        "transit": 0.2,
        "traffic": 0.3,
        "air_quality": 0.5,
        "weather": 0.6,
        "economics": 0.4,
        "crypto": 0.5,
        "geopolitical": 0.8,
        "digital": 0.3,
    }
    
    def calculate_amplification(
        self,
        domains: List[str],
        event_count: int,
        time_span_hours: float,
        radius_km: float,
    ) -> float:
        """Calculate total amplification factor"""
        amplification = 1.0
        
        # Domain diversity bonus
        unique_domains = set(domains)
        amplification *= 1 + (len(unique_domains) - 1) * 0.15
        
        # Domain combination multipliers
        for combo, mult in self.DOMAIN_MULTIPLIERS.items():
            if combo.issubset(unique_domains):
                amplification *= mult
        
        # Event count bonus (logarithmic)
        if event_count > 2:
            amplification *= 1 + math.log(event_count - 1) * 0.1
        
        # Time compression bonus (events close in time)
        if time_span_hours < 1:
            amplification *= 1.3
        elif time_span_hours < 3:
            amplification *= 1.2
        elif time_span_hours < 6:
            amplification *= 1.1
        
        # Spatial concentration bonus
        if radius_km < 50:
            amplification *= 1.2
        elif radius_km < 100:
            amplification *= 1.1
        
        # Domain weight average
        weights = [self.DOMAIN_WEIGHTS.get(d, 0.5) for d in unique_domains]
        if weights:
            avg_weight = sum(weights) / len(weights)
            amplification *= (0.5 + 0.5 * avg_weight)
        
        return min(amplification, 3.0)  # Cap at 3x


clusterer = SpatialTemporalClusterer()
correlator = CompoundEventCorrelator()
amplifier = SeverityAmplifier()