from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
import httpx

from app.models.user import User
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.config import settings


router = APIRouter()


class WeatherResponse(BaseModel):
    current: Dict[str, Any]
    hourly: List[Dict[str, Any]]
    daily: List[Dict[str, Any]]


class TransitVehicle(BaseModel):
    id: str
    route: str
    lat: float
    lon: float
    bearing: float
    speed: float
    updated: datetime


class AQIStation(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    pm25: Optional[float]
    pm10: Optional[float]
    no2: Optional[float]
    o3: Optional[float]
    aqi: Optional[int]
    updated: datetime


class WikiEdit(BaseModel):
    title: str
    user: str
    timestamp: datetime
    comment: str
    diff_url: str


class NewsArticle(BaseModel):
    title: str
    url: str
    source: str
    published: datetime
    tension_score: float
    location: str


class CityScopeResponse(BaseModel):
    city: str
    country: str
    lat: float
    lon: float
    weather: WeatherResponse
    transit: List[TransitVehicle]
    air_quality: List[AQIStation]
    wikipedia_pulse: List[WikiEdit]
    local_news: List[NewsArticle]


async def fetch_open_meteo(lat: float, lon: float) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.OPEN_METEO_URL}/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m",
                "hourly": "temperature_2m,precipitation_probability,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": 1,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


async def fetch_transitland(lat: float, lon: float, radius: int = 5000) -> list:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.TRANSITLAND_URL}/v1/vehicles",
            params={"lat": lat, "lon": lon, "r": radius, "per_page": 100},
            timeout=10,
        )
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        return resp.json().get("vehicles", [])


async def fetch_openaq(lat: float, lon: float, radius: int = 20000) -> list:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.OPENAQ_URL}/v2/latest",
            params={"coordinates": f"{lat},{lon}", "radius": radius, "limit": 100},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("results", [])


async def fetch_wikipedia_pulse(lat: float, lon: float, radius_km: int = 50) -> list:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://stream.wikimedia.org/v2/stream/recentchange",
            params={"since": int((datetime.utcnow() - timedelta(hours=1)).timestamp())},
            timeout=10,
        )
        return []


async def fetch_gdelt_news(lat: float, lon: float, radius_km: int = 50) -> list:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.GDELT_DOC_URL}/search",
            params={
                "lat": lat,
                "lon": lon,
                "radius": radius_km,
                "timespan": "24h",
                "format": "json",
                "maxrecords": 20,
            },
            timeout=10,
        )
        return []


@router.get("/{city_slug}", response_model=CityScopeResponse)
async def get_city_scope(
    city_slug: str,
    current_user: User = Depends(get_current_active_user),
):
    city_data = {
        "tokyo": {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503},
        "new-york": {"city": "New York", "country": "USA", "lat": 40.7128, "lon": -74.0060},
        "london": {"city": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278},
        "paris": {"city": "Paris", "country": "France", "lat": 48.8566, "lon": 2.3522},
        "sydney": {"city": "Sydney", "country": "Australia", "lat": -33.8688, "lon": 151.2093},
    }
    
    if city_slug not in city_data:
        raise HTTPException(status_code=404, detail="City not found")
    
    city = city_data[city_slug]
    lat, lon = city["lat"], city["lon"]
    
    weather, transit, aqi, wiki, news = await asyncio.gather(
        fetch_open_meteo(lat, lon),
        fetch_transitland(lat, lon),
        fetch_openaq(lat, lon),
        fetch_wikipedia_pulse(lat, lon),
        fetch_gdelt_news(lat, lon),
        return_exceptions=True
    )
    
    return CityScopeResponse(
        city=city["city"],
        country=city["country"],
        lat=lat,
        lon=lon,
        weather=weather if not isinstance(weather, Exception) else {},
        transit=[TransitVehicle(**v) for v in (transit if not isinstance(transit, Exception) else [])],
        air_quality=[AQIStation(**s) for s in (aqi if not isinstance(aqi, Exception) else [])],
        wikipedia_pulse=[WikiEdit(**e) for e in (wiki if not isinstance(wiki, Exception) else [])],
        local_news=[NewsArticle(**n) for n in (news if not isinstance(news, Exception) else [])],
    )