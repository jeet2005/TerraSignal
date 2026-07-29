from abc import ABC, abstractmethod
from datetime import datetime
from typing: List, Dict, Any
from app.models.event import Event
from app.core.logging import logger


class BaseIngestor(ABC):
    """Base class for all data ingestors"""
    
    def __init__(self, source: str, domain: str):
        self.source = source
        self.domain = domain
    
    @abstractmethod
    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetch raw data from the API"""
        pass
    
    @abstractmethod
    def normalize(self, raw_data: Dict[str, Any]) -> List[Event]:
        """Normalize raw data to Event objects"""
        pass
    
    async def ingest(self) -> List[Event]:
        """Run the full ingestion pipeline"""
        try:
            raw_data = await self.fetch()
            events = []
            if isinstance(raw_data, list):
                for item in raw_data:
                    normalized = self.normalize(item)
                    if normalized:
                        if isinstance(normalized, list):
                            events.extend(normalized)
                        else:
                            events.append(normalized)
            else:
                normalized = self.normalize(raw_data)
                if normalized:
                    if isinstance(normalized, list):
                        events.extend(normalized)
                    else:
                        events.append(normalized)
            
            logger.info(f"ingest_completed", source=self.source, domain=self.domain, count=len(events))
            return events
        except Exception as e:
            logger.error(f"ingest_failed", source=self.source, domain=self.domain, error=str(e))
            return []


class CompositeIngestor(BaseIngestor):
    """Ingestor that combines multiple sub-ingestors"""
    
    def __init__(self, ingestors: List[BaseIngestor]):
        super().__init__("composite", "mixed")
        self.ingestors = ingestors
    
    async def fetch(self) -> List[Dict[str, Any]]:
        # Not used for composite
        return []
    
    def normalize(self, raw_data: Dict[str, Any]) -> List[Event]:
        # Not used for composite
        return []
    
    async def ingest(self) -> List[Event]:
        all_events = []
        for ingestor in self.ingestors:
            events = await ingestor.ingest()
            all_events.extend(events)
        return all_events