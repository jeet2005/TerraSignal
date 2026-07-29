from datetime import datetime
from typing import List, Dict, Any
from app.services.ingest.base import BaseIngestor, APIIngestor, MultiAPIIngestor
from app.services.ingest.usgs import fetch_usgs_events, normalize_usgs_event
from app.services.ingest.open_meteo import fetch_open_meteo_weather, normalize_weather_event
from app.services.ingest.openaq import fetch_openaq_measurements, normalize_openaq_event
from app.services.ingest.nasa_firms import fetch_nasa_firms, normalize_firms_event
from app.services.ingest.nifc import fetch_nifc_fires, normalize_nifc_fire
from app.services.ingest.gdacs import fetch_gdacs_events, normalize_gdacs_event
from app.services.ingest.noaa_spc import fetch_noaa_spc_all, normalize_noaa_spc_event
from app.services.ingest.noaa_swpc import fetch_noaa_swpc_all, normalize_solar_flare, normalize_kp_index
from app.services.ingest.opensky import fetch_opensky_all, normalize_opensky_state
from app.services.ingest.ais import fetch_ais_all, normalize_ais_vessel
from app.services.ingest.transitland import fetch_transitland_feeds, normalize_transitland_feed
from app.services.ingest.tomtom import fetch_tomtom_incidents, normalize_tomtom_incident
from app.services.ingest.n2yo import fetch_n2yo_above, normalize_n2yo_satellite
from app.services.ingest.open_notify import fetch_iss_position, normalize_iss_position, fetch_astronauts, normalize_astronauts
from app.services.ingest.coingecko import fetch_coingecko_all, normalize_coingecko_coin, normalize_coingecko_global
from app.services.ingest.fred import fetch_fred_series, normalize_fred_observation, FRED_KEY_SERIES
from app.services.ingest.alpha_vantage import fetch_stock_quote, normalize_stock_quote, fetch_currency_exchange, normalize_currency_exchange
from app.services.ingest.exchangerate import fetch_exchange_rates, normalize_exchange_rates
from app.services.ingest.world_bank import fetch_world_bank_indicators, normalize_world_bank_data, WORLD_BANK_KEY_INDICATORS
from app.services.ingest.gdelt_geo import fetch_gdelt_geo, normalize_gdelt_geo
from app.services.ingest.gdelt_doc import fetch_gdelt_doc, normalize_gdelt_doc
from app.services.ingest.reliefweb import fetch_reliefweb_disasters, normalize_reliefweb_disaster, fetch_reliefweb_reports, normalize_reliefweb_report
from app.services.ingest.acled import fetch_acled_events, normalize_acled_event
from app.services.ingest.wikimedia import fetch_wikimedia_events, normalize_wikimedia_change
from app.services.ingest.github import fetch_github_events, normalize_github_event
from app.services.ingest.cloudflare import fetch_cloudflare_outages, normalize_cloudflare_outage
from app.services.ingest.hackernews import fetch_hn_top_stories, fetch_hn_batch, normalize_hn_item
from app.services.ingest.nominatim import geocode, normalize_nominatim_result
from app.core.config import settings
from app.core.logging import logger
from app.workers.ingestion_worker import worker
from app.models.event import Event


class APIIngestor(BaseIngestor):
    """Generic ingestor for APIs that fetch and normalize"""
    
    def __init__(self, source: str, domain: str, fetch_func, normalize_func, **fetch_kwargs):
        super().__init__(source, domain)
        self.fetch_func = fetch_func
        self.normalize_func = normalize_func
        self.fetch_kwargs = fetch_kwargs
    
    async def fetch(self) -> List[Dict[str, Any]]:
        return await self.fetch_func(**self.fetch_kwargs)
    
    def normalize(self, raw_data: Dict[str, Any]) -> List[Event]:
        event = self.normalize_func(raw_data)
        return [event] if event else []


class MultiAPIIngestor(BaseIngestor):
    """Ingestor that fetches from multiple API endpoints"""
    
    def __init__(self, source: str, domain: str, fetch_func, normalize_funcs: Dict[str, callable]):
        super().__init__(source, domain)
        self.fetch_func = fetch_func
        self.normalize_funcs = normalize_funcs
    
    async def fetch(self) -> List[Dict[str, Any]]:
        return await self.fetch_func()
    
    def normalize(self, raw_data: Dict[str, Any]) -> List[Event]:
        events = []
        for key, normalize_func in self.normalize_funcs.items():
            data = raw_data.get(key, [])
            if isinstance(data, list):
                for item in data:
                    event = normalize_func(item)
                    if event:
                        events.append(event)
            else:
                event = normalize_func(data)
                if event:
                    events.append(event)
        return events


async def initialize_ingestion_worker():
    """Initialize and configure all ingestors with the worker"""
    
    # ============================================================
    # ENVIRONMENT & CLIMATE (high frequency - every 5 min)
    # ============================================================
    worker.add_ingestor(
        APIIngestor("usgs", "seismic", fetch_usgs_events, normalize_usgs_event),
        interval_seconds=300,  # 5 min
        job_id="ingest_usgs"
    )
    
    worker.add_ingestor(
        APIIngestor("nasa_firms", "fire", fetch_nasa_firms, normalize_firms_event),
        interval_seconds=300,  # 5 min
        job_id="ingest_nasa_firms"
    )
    
    worker.add_ingestor(
        APIIngestor("openaq", "air_quality", fetch_openaq_measurements, normalize_openaq_event, lat=0, lon=0, radius=20000000),
        interval_seconds=300,  # 5 min
        job_id="ingest_openaq"
    )
    
    worker.add_ingestor(
        APIIngestor("open_meteo", "weather", fetch_open_meteo_weather, normalize_weather_event, lat=0, lon=0),
        interval_seconds=300,  # 5 min
        job_id="ingest_open_meteo"
    )
    
    # ============================================================
    # DISASTER ALERTS (every 10 min)
    # ============================================================
    worker.add_ingestor(
        APIIngestor("gdacs", "disaster", fetch_gdacs_events, normalize_gdacs_event),
        interval_seconds=600,  # 10 min
        job_id="ingest_gdacs"
    )
    
    worker.add_ingestor(
        APIIngestor("nifc", "fire", fetch_nifc_fires, normalize_nifc_fire),
        interval_seconds=600,  # 10 min
        job_id="ingest_nifc"
    )
    
    worker.add_ingestor(
        APIIngestor("noaa_spc", "storm", fetch_noaa_spc_all, normalize_noaa_spc_event),
        interval_seconds=600,  # 10 min
        job_id="ingest_noaa_spc"
    )
    
    worker.add_ingestor(
        MultiAPIIngestor(
            "noaa_swpc", "space_weather", fetch_noaa_swpc_all,
            {"flares": normalize_solar_flare, "kp": normalize_kp_index}
        ),
        interval_seconds=600,  # 10 min
        job_id="ingest_noaa_swpc"
    )
    
    # ============================================================
    # MOVEMENT (high frequency for live tracking)
    # ============================================================
    worker.add_ingestor(
        APIIngestor("opensky", "aviation", fetch_opensky_all, normalize_opensky_state),
        interval_seconds=30,  # 30 sec
        job_id="ingest_opensky"
    )
    
    worker.add_ingestor(
        APIIngestor("ais", "maritime", fetch_ais_all, normalize_ais_vessel),
        interval_seconds=60,  # 1 min
        job_id="ingest_ais"
    )
    
    # ============================================================
    # TRANSIT (every 5 min)
    # ============================================================
    worker.add_ingestor(
        APIIngestor("transitland", "transit", fetch_transitland_feeds, normalize_transitland_feed),
        interval_seconds=300,  # 5 min
        job_id="ingest_transitland"
    )
    
    # ============================================================
    # SPACE (ISS every 30 sec, astronauts every 5 min)
    # ============================================================
    worker.add_ingestor(
        APIIngestor("open_notify", "space", fetch_iss_position, normalize_iss_position),
        interval_seconds=30,  # 30 sec
        job_id="ingest_iss"
    )
    
    worker.add_ingestor(
        APIIngestor("open_notify_astronauts", "space", fetch_astronauts, normalize_astronauts),
        interval_seconds=300,  # 5 min
        job_id="ingest_astronauts"
    )
    
    # ============================================================
    # ECONOMICS (crypto every 5 min, traditional every 15 min)
    # ============================================================
    worker.add_ingestor(
        MultiAPIIngestor(
            "coingecko", "crypto", fetch_coingecko_all,
            {"markets": normalize_coingecko_coin, "global": normalize_coingecko_global}
        ),
        interval_seconds=300,  # 5 min
        job_id="ingest_coingecko"
    )
    
    # FRED key series (every 15 min)
    for series_id, series_name in list(FRED_KEY_SERIES.items())[:10]:
        worker.add_ingestor(
            APIIngestor(f"fred_{series_id}", "economics", fetch_fred_series, normalize_fred_observation, series_id=series_id),
            interval_seconds=900,  # 15 min
            job_id=f"ingest_fred_{series_id}"
        )
    
    # Alpha Vantage (every 5 min for stocks, 15 min for forex)
    worker.add_ingestor(
        APIIngestor("alpha_vantage_spy", "economics", fetch_stock_quote, normalize_stock_quote, symbol="SPY"),
        interval_seconds=300,  # 5 min
        job_id="ingest_alpha_vantage_spy"
    )
    
    worker.add_ingestor(
        APIIngestor("exchangerate", "economics", fetch_exchange_rates, normalize_exchange_rates, base="USD"),
        interval_seconds=900,  # 15 min
        job_id="ingest_exchangerate"
    )
    
    # World Bank (every 30 min - slow changing)
    for indicator_code, indicator_name in list(WORLD_BANK_KEY_INDICATORS.items())[:5]:
        worker.add_ingestor(
            APIIngestor(f"world_bank_{indicator_code}", "economics", fetch_world_bank_indicators, normalize_world_bank_data, indicator=indicator_code),
            interval_seconds=1800,  # 30 min
            job_id=f"ingest_world_bank_{indicator_code}"
        )
    
    # ============================================================
    # GEOPOLITICAL (every 15 min)
    # ============================================================
    worker.add_ingestor(
        APIIngestor("gdelt_geo", "geopolitical", fetch_gdelt_geo, normalize_gdelt_geo),
        interval_seconds=900,  # 15 min
        job_id="ingest_gdelt_geo"
    )
    
    worker.add_ingestor(
        APIIngestor("gdelt_doc", "geopolitical", fetch_gdelt_doc, normalize_gdelt_doc),
        interval_seconds=900,  # 15 min
        job_id="ingest_gdelt_doc"
    )
    
    worker.add_ingestor(
        APIIngestor("reliefweb", "humanitarian", fetch_reliefweb_disasters, normalize_reliefweb_disaster),
        interval_seconds=900,  # 15 min
        job_id="ingest_reliefweb"
    )
    
    worker.add_ingestor(
        APIIngestor("acled", "conflict", fetch_acled_events, normalize_acled_event),
        interval_seconds=900,  # 15 min
        job_id="ingest_acled"
    )
    
    # ============================================================
    # DIGITAL WORLD (every 5 min)
    # ============================================================
    worker.add_ingestor(
        APIIngestor("wikimedia", "digital", fetch_wikimedia_events, normalize_wikimedia_change),
        interval_seconds=300,  # 5 min
        job_id="ingest_wikimedia"
    )
    
    worker.add_ingestor(
        APIIngestor("github", "digital", fetch_github_events, normalize_github_event),
        interval_seconds=300,  # 5 min
        job_id="ingest_github"
    )
    
    worker.add_ingestor(
        APIIngestor("cloudflare_radar", "digital", fetch_cloudflare_outages, normalize_cloudflare_outage),
        interval_seconds=300,  # 5 min
        job_id="ingest_cloudflare"
    )
    
    worker.add_ingestor(
        APIIngestor("hackernews", "digital", fetch_hn_top_stories, normalize_hn_item),
        interval_seconds=300,  # 5 min
        job_id="ingest_hackernews"
    )
    
    # ============================================================
    # SATELLITE TRACKING (every 5 min)
    # ============================================================
    worker.add_ingestor(
        APIIngestor("n2yo", "space", fetch_n2yo_above, normalize_n2yo_satellite, lat=0, lon=0, alt=0, radius=90, category=0),
        interval_seconds=300,  # 5 min
        job_id="ingest_n2yo"
    )
    
    # ============================================================
    # TRAFFIC (every 5 min)
    # ============================================================
    worker.add_ingestor(
        APIIngestor("tomtom", "traffic", fetch_tomtom_incidents, normalize_tomtom_incident),
        interval_seconds=300,  # 5 min
        job_id="ingest_tomtom"
    )
    
    worker.start()
    logger.info("all_ingestors_initialized", total_jobs=len(worker.ingestors))


async def run_initial_ingestion():
    """Run initial ingestion for all APIs on startup"""
    logger.info("starting_initial_ingestion")
    
    # USGS Earthquakes
    try:
        events = await fetch_usgs_events()
        normalized = [normalize_usgs_event(e) for e in events if normalize_usgs_event(e)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("usgs_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("usgs_initial_failed", error=str(e))
    
    # NASA FIRMS
    try:
        fires = await fetch_nasa_firms()
        normalized = [normalize_firms_event(f) for f in fires if normalize_firms_event(f)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("nasa_firms_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("nasa_firms_initial_failed", error=str(e))
    
    # OpenAQ
    try:
        measurements = await fetch_openaq_measurements(0, 0, 20000000)
        normalized = [normalize_openaq_event(m) for m in measurements if normalize_openaq_event(m)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("openaq_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("openaq_initial_failed", error=str(e))
    
    # GDACS
    try:
        events = await fetch_gdacs_events()
        normalized = [normalize_gdacs_event(e) for e in events if normalize_gdacs_event(e)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("gdacs_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("gdacs_initial_failed", error=str(e))
    
    # NOAA SPC
    try:
        outlooks = await fetch_noaa_spc_all()
        normalized = [normalize_noaa_spc_event(o) for o in outlooks if normalize_noaa_spc_event(o)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("noaa_spc_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("noaa_spc_initial_failed", error=str(e))
    
    # NOAA SWPC
    try:
        swpc_data = await fetch_noaa_swpc_all()
        flares = [normalize_solar_flare(f) for f in swpc_data.get("flares", []) if normalize_solar_flare(f)]
        kp = [normalize_kp_index(k) for k in swpc_data.get("kp", []) if normalize_kp_index(k)]
        all_swpc = flares + kp
        if all_swpc:
            await Event.insert_many(all_swpc)
            logger.info("noaa_swpc_initial_ingested", count=len(all_swpc))
    except Exception as e:
        logger.error("noaa_swpc_initial_failed", error=str(e))
    
    # CoinGecko
    try:
        coingecko_data = await fetch_coingecko_all()
        coins = [normalize_coingecko_coin(c) for c in coingecko_data.get("markets", []) if normalize_coingecko_coin(c)]
        global_data = normalize_coingecko_global(coingecko_data.get("global", {}))
        all_coin = coins + ([global_data] if global_data else [])
        if all_coin:
            await Event.insert_many(all_coin)
            logger.info("coingecko_initial_ingested", count=len(all_coin))
    except Exception as e:
        logger.error("coingecko_initial_failed", error=str(e))
    
    # OpenSky
    try:
        states = await fetch_opensky_all()
        normalized = [normalize_opensky_state(s) for s in states if normalize_opensky_state(s)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("opensky_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("opensky_initial_failed", error=str(e))
    
    # AIS
    try:
        vessels = await fetch_ais_all()
        normalized = [normalize_ais_vessel(v) for v in vessels if normalize_ais_vessel(v)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("ais_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("ais_initial_failed", error=str(e))
    
    # Transitland
    try:
        feeds = await fetch_transitland_feeds()
        normalized = [normalize_transitland_feed(f) for f in feeds if normalize_transitland_feed(f)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("transitland_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("transitland_initial_failed", error=str(e))
    
    # ISS
    try:
        iss = await fetch_iss_position()
        if iss:
            event = normalize_iss_position(iss)
            if event:
                await event.insert()
                logger.info("iss_initial_ingested")
    except Exception as e:
        logger.error("iss_initial_failed", error=str(e))
    
    # GDELT Geo
    try:
        features = await fetch_gdelt_geo()
        normalized = [normalize_gdelt_geo(f) for f in features if normalize_gdelt_geo(f)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("gdelt_geo_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("gdelt_geo_initial_failed", error=str(e))
    
    # GDELT Doc
    try:
        articles = await fetch_gdelt_doc()
        normalized = [normalize_gdelt_doc(a) for a in articles if normalize_gdelt_doc(a)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("gdelt_doc_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("gdelt_doc_initial_failed", error=str(e))
    
    # ReliefWeb
    try:
        disasters = await fetch_reliefweb_disasters()
        normalized = [normalize_reliefweb_disaster(d) for d in disasters if normalize_reliefweb_disaster(d)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("reliefweb_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("reliefweb_initial_failed", error=str(e))
    
    # Wikimedia
    try:
        changes = await fetch_wikimedia_events(50)
        normalized = [normalize_wikimedia_change(c) for c in changes if normalize_wikimedia_change(c)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("wikimedia_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("wikimedia_initial_failed", error=str(e))
    
    # GitHub
    try:
        events = await fetch_github_events()
        normalized = [normalize_github_event(e) for e in events if normalize_github_event(e)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("github_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("github_initial_failed", error=str(e))
    
    # Cloudflare
    try:
        outages = await fetch_cloudflare_outages()
        normalized = [normalize_cloudflare_outage(o) for o in outages if normalize_cloudflare_outage(o)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("cloudflare_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("cloudflare_initial_failed", error=str(e))
    
    # Hacker News
    try:
        top_stories = await fetch_hn_top_stories()
        items = await fetch_hn_batch(top_stories[:20])
        normalized = [normalize_hn_item(i) for i in items if normalize_hn_item(i)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("hackernews_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("hackernews_initial_failed", error=str(e))
    
    # N2YO
    try:
        sats = await fetch_n2yo_above(0, 0, 0, 90, 0)
        normalized = [normalize_n2yo_satellite(s) for s in sats if normalize_n2yo_satellite(s)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("n2yo_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("n2yo_initial_failed", error=str(e))
    
    # TomTom
    try:
        incidents = await fetch_tomtom_incidents()
        normalized = [normalize_tomtom_incident(i) for i in incidents if normalize_tomtom_incident(i)]
        if normalized:
            await Event.insert_many(normalized)
            logger.info("tomtom_initial_ingested", count=len(normalized))
    except Exception as e:
        logger.error("tomtom_initial_failed", error=str(e))
    
    logger.info("initial_ingestion_completed")