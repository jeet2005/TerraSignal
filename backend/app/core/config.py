import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "TerraSignal"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    API_V1_STR: str = "/api/v1"
    
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "terrasignal"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    USGS_EARTHQUAKE_URL: str = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1"
    OPENAQ_URL: str = "https://api.openaq.org/v2"
    NASA_FIRMS_URL: str = "https://firms.modaps.eosdis.nasa.gov/api"
    GDACS_URL: str = "https://www.gdacs.org/gdacsapi/api"
    NOAA_SPC_URL: str = "https://www.spc.noaa.gov/products/outlook"
    NOAA_SWPC_URL: str = "https://services.swpc.noaa.gov/json"
    OPENSKY_URL: str = "https://opensky-network.org/api"
    AIS_URL: str = "https://api.ais.52north.org"
    TRANSITLAND_URL: str = "https://transit.land/api"
    TOMTOM_URL: str = "https://api.tomtom.com/traffic/services/4"
    N2YO_URL: str = "https://api.n2yo.com/rest/v1/satellite"
    OPEN_NOTIFY_URL: str = "http://api.open-notify.org"
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3"
    FRED_URL: str = "https://api.stlouisfed.org/fred"
    ALPHA_VANTAGE_URL: str = "https://www.alphavantage.co/query"
    EXCHANGE_RATE_URL: str = "https://api.exchangerate-api.com/v4"
    WORLD_BANK_URL: str = "https://api.worldbank.org/v2"
    COMMODITY_URL: str = "https://api.commodityprices.com/v1"
    GDELT_GEO_URL: str = "https://api.gdeltproject.org/api/v2/geo"
    GDELT_DOC_URL: str = "https://api.gdeltproject.org/api/v2/doc"
    RELIEFWEB_URL: str = "https://api.reliefweb.int/v1"
    ACLED_URL: str = "https://api.acleddata.com"
    WIKIMEDIA_EVENTSTREAM_URL: str = "https://stream.wikimedia.org/v2/stream"
    GITHUB_EVENTS_URL: str = "https://api.github.com/events"
    CLOUDFLARE_RADAR_URL: str = "https://radar.cloudflare.com/api"
    HACKER_NEWS_URL: str = "https://hacker-news.firebaseio.com/v0"
    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org"
    
    CESIUM_ION_TOKEN: str = ""
    
    VAPID_PUBLIC_KEY: str = ""
    VAPID_PRIVATE_KEY: str = ""
    VAPID_CLAIMS_EMAIL: str = "alerts@terrasignal.io"
    
    WORKER_CONCURRENCY: int = 4
    FETCH_INTERVAL_SECONDS: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()