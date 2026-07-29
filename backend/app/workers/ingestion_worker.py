from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing: List, Dict, Any
from app.core.logging import logger
from app.models.event import Event


class IngestionWorker:
    """APScheduler-based worker for periodic data ingestion"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.ingestors: List[Dict[str, Any]] = []
    
    def add_ingestor(self, ingestor, interval_seconds: int, job_id: str):
        """Add an ingestor to the scheduler"""
        self.ingestors.append({
            "ingestor": ingestor,
            "interval_seconds": interval_seconds,
            "job_id": job_id
        })
    
    async def run_ingestion(self, ingestor, job_id: str):
        """Run a single ingestion job"""
        start_time = datetime.utcnow()
        logger.info("ingestion_started", job_id=job_id, source=ingestor.source)
        
        try:
            events = await ingestor.ingest()
            if events:
                await Event.insert_many(events)
                logger.info(
                    "ingestion_completed",
                    job_id=job_id,
                    source=ingestor.source,
                    domain=ingestor.domain,
                    events_count=len(events),
                    duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
            else:
                logger.info("ingestion_no_events", job_id=job_id, source=ingestor.source)
        except Exception as e:
            logger.error("ingestion_failed", job_id=job_id, source=ingestor.source, error=str(e))
    
    def start(self):
        """Start the scheduler with all ingestors"""
        for item in self.ingestors:
            ingestor = item["ingestor"]
            interval = item["interval_seconds"]
            job_id = item["job_id"]
            
            self.scheduler.add_job(
                self.run_ingestion,
                trigger=IntervalTrigger(seconds=interval),
                args=[ingestor, job_id],
                id=job_id,
                replace_existing=True,
                max_instances=1,
                coalesce=True
            )
            
            # Run once immediately on startup
            self.scheduler.add_job(
                self.run_ingestion,
                args=[ingestor, job_id],
                id=f"{job_id}_initial",
                replace_existing=True
            )
        
        self.scheduler.start()
        logger.info("ingestion_worker_started", jobs=len(self.ingestors))
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("ingestion_worker_stopped")


# Global worker instance
worker = IngestionWorker()