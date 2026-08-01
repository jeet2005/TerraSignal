from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TerraSignal"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"
    DEBUG: bool = True

    # Database
    POSTGRES_DB: str = "terrasignal"
    POSTGRES_USER: str = "terrasignal"
    POSTGRES_PASSWORD: str = "terrasignal"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://terrasignal:terrasignal@localhost:5432/terrasignal"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Keys - Environment & Climate
    USGS_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    OPENAQ_API_KEY: str = ""
    NASA_FIRMS_API_KEY: str = ""
    NOAA_API_KEY: str = ""

    # API Keys - Movement
    OPENSKY_CLIENT_ID: str = ""
    OPENSKY_CLIENT_SECRET: str = ""
    AIS_API_KEY: str = ""
    TRANSITLAND_API_KEY: str = ""
    TOMTOM_API_KEY: str = ""

    # API Keys - Space
    N2YO_API_KEY: str = ""

    # API Keys - Economics
    COINGECKO_API_KEY: str = ""
    FRED_API_KEY: str = ""
    ALPHAVANTAGE_API_KEY: str = ""
    EXCHANGERATE_API_KEY: str = ""
    WORLD_BANK_API_KEY: str = ""
    COMMODITY_API_KEY: str = ""

    # API Keys - Humanitarian
    GDELT_API_KEY: str = ""
    RELIEFWEB_API_KEY: str = ""
    ACLED_API_KEY: str = ""

    # API Keys - Digital World
    CLOUDFLARE_RADAR_API_KEY: str = ""

    # Frontend
    MAPBOX_TOKEN: str = ""

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@terrasignal.io"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Data Ingestion
    INGESTION_INTERVAL_SECONDS: int = 60
    MAX_CONCURRENT_INGESTIONS: int = 10
    REQUEST_TIMEOUT_SECONDS: int = 30

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 10000

    # Correlation Engine
    CORRELATION_SPATIAL_RADIUS_KM: float = 150.0
    CORRELATION_TIME_WINDOW_HOURS: int = 6
    CORRELATION_MIN_DOMAINS: int = 2
    SEVERITY_AMPLIFICATION_2_DOMAINS: float = 1.3
    SEVERITY_AMPLIFICATION_3_DOMAINS: float = 1.7
    SEVERITY_AMPLIFICATION_4_PLUS_DOMAINS: float = 2.2

    # Anomaly Detection
    ANOMALY_LOOKBACK_DAYS: int = 7
    ANOMALY_ZSCORE_THRESHOLD: float = 3.0
    ANOMALY_MIN_SAMPLES: int = 10

    # Anomaly thresholds
    ANOMALY_ZSCORE_THRESHOLD_LOW: float = 2.0
    ANOMALY_ZSCORE_THRESHOLD_HIGH: float = 3.5
    ANOMALY_MIN_OBSERVATIONS: int = 10

    # Severity thresholds
    SEVERITY_LOW: float = 0.3
    SEVERITY_MEDIUM: float = 0.5
    SEVERITY_HIGH: float = 0.7
    SEVERITY_CRITICAL: float = 0.85

    # Alert thresholds
    ALERT_SEVERITY_THRESHOLD: float = 0.7
    ALERT_COOLDOWN_MINUTES: int = 30

    # Mapbox
    MAPBOX_TOKEN: str = ""

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()