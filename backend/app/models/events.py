import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    Float,
    Integer,
    DateTime,
    Boolean,
    Enum,
    ForeignKey,
    Index,
    Text,
    JSON,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class DomainType(str, enum.Enum):
    ENVIRONMENT = "environment"
    MOVEMENT = "movement"
    SPACE_WEATHER = "space_weather"
    ECONOMICS = "economics"
    HUMANITARIAN = "humanitarian"
    DIGITAL = "digital"


class EventType(str, enum.Enum):
    # Environment
    EARTHQUAKE = "earthquake"
    WILDFIRE = "wildfire"
    WILDFIRE_PERIMETER = "wildfire_perimeter"
    AIR_QUALITY = "air_quality"
    WEATHER = "weather"
    STORM_OUTLOOK = "storm_outlook"
    VOLCANIC_ACTIVITY = "volcanic_activity"
    FLOOD = "flood"
    DROUGHT = "drought"
    CYCLONE = "cyclone"
    TSUNAMI = "tsunami"

    # Movement
    FLIGHT = "flight"
    FLIGHT_TRAIL = "flight_trail"
    SHIP = "ship"
    SHIPPING_LANE = "shipping_lane"
    TRANSIT_VEHICLE = "transit_vehicle"
    TRAFFIC = "traffic"
    SATELLITE = "satellite"
    ISS = "iss"

    # Space Weather
    SOLAR_FLARE = "solar_flare"
    GEOMAGNETIC_STORM = "geomagnetic_storm"
    CME = "coronal_mass_ejection"
    SOLAR_WIND = "solar_wind"
    RADIATION_BELT = "radiation_belt"

    # Economics
    CRYPTO_PRICE = "crypto_price"
    CRYPTO_VOLATILITY = "crypto_volatility"
    GOLD_PRICE = "gold_price"
    CURRENCY_RATE = "currency_rate"
    REMITTANCE_CORRIDOR = "remittance_corridor"
    MACRO_INDICATOR = "macro_indicator"
    MARKET_VOLATILITY = "market_volatility"
    COMMODITY_PRICE = "commodity_price"
    GDP_INDICATOR = "gdp_indicator"

    # Humanitarian
    NEWS_EVENT = "news_event"
    CONFLICT_EVENT = "conflict_event"
    DISASTER_DECLARATION = "disaster_declaration"
    REFUGEE_REPORT = "refugee_report"
    LOCAL_NEWS = "local_news"

    # Digital
    WIKIPEDIA_EDIT = "wikipedia_edit"
    WIKIPEDIA_PULSE = "wikipedia_pulse"
    GITHUB_ACTIVITY = "github_activity"
    INTERNET_OUTAGE = "internet_outage"
    HACKER_NEWS = "hacker_news"


class SeverityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(str, enum.Enum):
    ACTIVE = "active"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class Event(BaseModel):
    __tablename__ = "events"

    event_type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False, index=True)
    domain: Mapped[DomainType] = mapped_column(Enum(DomainType), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    location_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(3), nullable=True, index=True)
    admin1: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    admin2: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    severity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, index=True)
    severity_level: Mapped[SeverityLevel] = mapped_column(Enum(SeverityLevel), nullable=False, default=SeverityLevel.LOW, index=True)

    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus), nullable=False, default=EventStatus.ACTIVE, index=True)

    magnitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    depth: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    area_km2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at_source: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    raw_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    is_anomaly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    anomaly_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    anomaly_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    compound_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("compound_events.id"), nullable=True, index=True)

    __table_args__ = (
        Index("ix_events_spatial", "latitude", "longitude"),
        Index("ix_events_domain_time", "domain", "started_at"),
        Index("ix_events_type_time", "event_type", "started_at"),
        Index("ix_events_severity_time", "severity", "started_at"),
    )

    compound_event: Mapped[Optional["CompoundEvent"]] = relationship(back_populates="events")
    anomalies: Mapped[list["Anomaly"]] = relationship(back_populates="event", cascade="all, delete-orphan")


class CompoundEvent(BaseModel):
    __tablename__ = "compound_events"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    location_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(3), nullable=True, index=True)

    severity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, index=True)
    severity_level: Mapped[SeverityLevel] = mapped_column(Enum(SeverityLevel), nullable=False, default=SeverityLevel.LOW, index=True)

    domain_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    domains: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    event_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus), nullable=False, default=EventStatus.ACTIVE, index=True)

    contributing_events: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    news_headlines: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    amplification_factor: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    __table_args__ = (
        Index("ix_compound_events_spatial", "latitude", "longitude"),
        Index("ix_compound_events_severity_time", "severity", "started_at"),
    )

    events: Mapped[list[Event]] = relationship(back_populates="compound_event", cascade="all, delete-orphan")


class Anomaly(BaseModel):
    __tablename__ = "anomalies"

    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    domain: Mapped[DomainType] = mapped_column(Enum(DomainType), nullable=False, index=True)

    value: Mapped[float] = mapped_column(Float, nullable=False)
    expected_value: Mapped[float] = mapped_column(Float, nullable=False)
    std_deviation: Mapped[float] = mapped_column(Float, nullable=False)
    z_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    anomaly_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, default=func.now())
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    context: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    event: Mapped[Event] = relationship(back_populates="anomalies")

    __table_args__ = (
        Index("ix_anomalies_domain_time", "domain", "detected_at"),
        Index("ix_anomalies_metric_time", "metric_name", "detected_at"),
    )


class DataSource(BaseModel):
    __tablename__ = "data_sources"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    domain: Mapped[DomainType] = mapped_column(Enum(DomainType), nullable=False, index=True)

    api_url: Mapped[str] = mapped_column(String(500), nullable=False)
    api_key_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, nullable=False, default=60)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_healthy: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_successful_fetch: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    ingestion_runs: Mapped[list["IngestionRun"]] = relationship(back_populates="source", cascade="all, delete-orphan")


class IngestionRun(BaseModel):
    __tablename__ = "ingestion_runs"

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_sources.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)

    events_fetched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    events_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    events_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    events_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    source: Mapped[DataSource] = relationship(back_populates="ingestion_runs")

    __table_args__ = (
        Index("ix_ingestion_runs_source_time", "source_id", "started_at"),
    )


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    preferences: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    alert_preferences: Mapped[list["AlertPreference"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    push_subscriptions: Mapped[list["PushSubscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class AlertPreference(BaseModel):
    __tablename__ = "alert_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    domain: Mapped[Optional[DomainType]] = mapped_column(Enum(DomainType), nullable=True, index=True)
    event_type: Mapped[Optional[EventType]] = mapped_column(Enum(EventType), nullable=True, index=True)
    min_severity: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    location_filter: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    notify_push: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notify_email: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notify_in_app: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped[User] = relationship(back_populates="alert_preferences")


class PushSubscription(BaseModel):
    __tablename__ = "push_subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    p256dh: Mapped[str] = mapped_column(String(200), nullable=False)
    auth: Mapped[str] = mapped_column(String(200), nullable=False)

    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped[User] = relationship(back_populates="push_subscriptions")


class Alert(BaseModel):
    __tablename__ = "alerts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("events.id"), nullable=True, index=True)
    compound_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("compound_events.id"), nullable=True, index=True)
    anomaly_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("anomalies.id"), nullable=True, index=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[float] = mapped_column(Float, nullable=False)

    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    sent_push: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sent_email: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship()
    event: Mapped[Optional[Event]] = relationship()
    compound_event: Mapped[Optional[CompoundEvent]] = relationship()
    anomaly: Mapped[Optional[Anomaly]] = relationship()

    __table_args__ = (
        Index("ix_alerts_user_unread", "user_id", "is_read", "is_dismissed"),
    )


class CityScopeData(BaseModel):
    __tablename__ = "city_scope_data"

    city_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    country_code: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    weather_current: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    weather_forecast: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    transit_vehicles: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    transit_agencies: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    air_quality_stations: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    wikipedia_edits_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wikipedia_articles: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    local_news: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    __table_args__ = (
        Index("ix_city_scope_city_country", "city_name", "country_code"),
    )


class EconomicIndicator(BaseModel):
    __tablename__ = "economic_indicators"

    indicator_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    indicator_name: Mapped[str] = mapped_column(String(200), nullable=False)
    country_code: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    country_name: Mapped[str] = mapped_column(String(100), nullable=False)

    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)

    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)

    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_economic_indic_country_date", "country_code", "date"),
        Index("ic_indicator_date", "indicator_code", "date"),
    )


class CryptoPrice(BaseModel):
    __tablename__ = "crypto_prices"

    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    price_usd: Mapped[float] = mapped_column(Float, nullable=False)
    market_cap_usd: Mapped[float] = mapped_column(Float, nullable=False)
    volume_24h_usd: Mapped[float] = mapped_column(Float, nullable=False)
    change_24h_pct: Mapped[float] = mapped_column(Float, nullable=False)
    change_1h_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_crypto_rank_time", "rank", "last_updated"),
    )


class CurrencyRate(BaseModel):
    __tablename__ = "currency_rates"

    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    rate: Mapped[float] = mapped_column(Float, nullable=False)

    change_24h_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_remittance_corridor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_currency_pair_time", "base_currency", "quote_currency", "timestamp"),
    )


class CommodityPrice(BaseModel):
    __tablename__ = "commodity_prices"

    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    price: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    change_24h_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    change_30d_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_commodity_symbol_time", "symbol", "timestamp"),
    )


class WikiEdit(BaseModel):
    __tablename__ = "wiki_edits"

    page_title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    page_id: Mapped[int] = mapped_column(Integer, nullable=False)
    editor: Mapped[str] = mapped_column(String(200), nullable=False)
    is_bot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    is_minor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_new: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    diff_url: Mapped[str] = mapped_column(String(500), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    byte_change: Mapped[int] = mapped_column(Integer, nullable=False)

    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(3), nullable=True, index=True)
    city_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_wiki_edits_geo_time", "latitude", "longitude", "timestamp"),
        Index("ix_wiki_edits_city_time", "city_name", "timestamp"),
    )


class InternetHealth(BaseModel):
    __tablename__ = "internet_health"

    country_code: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    country_name: Mapped[str] = mapped_column(String(100), nullable=False)

    traffic_score: Mapped[float] = mapped_column(Float, nullable=False)
    outage_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    outage_severity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    throughput_mbps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_internet_health_country_time", "country_code", "timestamp"),
    )


class GitHubActivity(BaseModel):
    __tablename__ = "github_activity"

    repo_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    repo_owner: Mapped[str] = mapped_column(String(100), nullable=False)
    repo_url: Mapped[str] = mapped_column(String(500), nullable=False)

    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(200), nullable=False)

    commits_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    issues_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    prs_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stars_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_github_repo_time", "repo_name", "timestamp"),
    )


class HackerNewsStory(BaseModel):
    __tablename__ = "hacker_news_stories"

    hn_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    author: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    descendants: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    story_type: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    is_trending: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)


class SatellitePass(BaseModel):
    __tablename__ = "satellite_passes"

    satellite_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    satellite_name: Mapped[str] = mapped_column(String(200), nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    altitude_km: Mapped[float] = mapped_column(Float, nullable=False)

    azimuth: Mapped[float] = mapped_column(Float, nullable=False)
    elevation: Mapped[float] = mapped_column(Float, nullable=False)

    magnitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    observer_lat: Mapped[float] = mapped_column(Float, nullable=False)
    observer_lon: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        Index("ix_sat_passes_observer_time", "observer_lat", "observer_lon", "start_time"),
    )


class ISSPosition(BaseModel):
    __tablename__ = "iss_positions"

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    altitude_km: Mapped[float] = mapped_column(Float, nullable=False)
    velocity_kmh: Mapped[float] = mapped_column(Float, nullable=False)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    crew_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    crew_names: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    __table_args__ = (
        Index("ix_iss_time", "timestamp"),
    )


class SpaceWeather(BaseModel):
    __tablename__ = "space_weather"

    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)

    kp_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    solar_flare_class: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    cme_speed_kms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    message: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)

    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_space_weather_type_time", "event_type", "issued_at"),
    )


class HealthCheck(BaseModel):
    __tablename__ = "health_checks"

    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)