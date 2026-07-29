from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

from app.models.user import User
from app.api.v1.endpoints.auth import get_current_active_user


router = APIRouter()


class SettingsResponse(BaseModel):
    alert_threshold: float
    default_layers: List[str]
    units: str
    offline_mode: bool
    map_style: str
    auto_refresh: bool
    refresh_interval: int
    voice_enabled: bool
    language: str


class SettingsUpdate(BaseModel):
    alert_threshold: Optional[float] = None
    default_layers: Optional[List[str]] = None
    units: Optional[str] = None
    offline_mode: Optional[bool] = None
    map_style: Optional[str] = None
    auto_refresh: Optional[bool] = None
    refresh_interval: Optional[int] = None
    voice_enabled: Optional[bool] = None
    language: Optional[str] = None


@router.get("", response_model=SettingsResponse)
async def get_settings(current_user: User = Depends(get_current_active_user)):
    return SettingsResponse(
        alert_threshold=current_user.alert_threshold,
        default_layers=current_user.default_layers,
        units=current_user.units,
        offline_mode=current_user.offline_mode,
        map_style=current_user.map_style,
        auto_refresh=current_user.auto_refresh,
        refresh_interval=current_user.refresh_interval,
        voice_enabled=current_user.voice_enabled,
        language=current_user.language,
    )


@router.patch("", response_model=SettingsResponse)
async def update_settings(
    settings: SettingsUpdate,
    current_user: User = Depends(get_current_active_user),
):
    update_data = settings.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    return SettingsResponse(
        alert_threshold=current_user.alert_threshold,
        default_layers=current_user.default_layers,
        units=current_user.units,
        offline_mode=current_user.offline_mode,
        map_style=current_user.map_style,
        auto_refresh=current_user.auto_refresh,
        refresh_interval=current_user.refresh_interval,
        voice_enabled=current_user.voice_enabled,
        language=current_user.language,
    )