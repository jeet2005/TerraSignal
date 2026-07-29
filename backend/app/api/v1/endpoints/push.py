from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pywebpush import webpush, WebPushException

from app.models.push import PushSubscription
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.config import get_settings


router = APIRouter()
settings = get_settings()


class SubscriptionRequest(BaseModel):
    endpoint: str
    keys: dict
    user_agent: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: str
    endpoint: str
    active: bool
    created_at: datetime


class PushPayload(BaseModel):
    title: str
    body: str
    icon: Optional[str] = "/icons/alert-192.png"
    badge: Optional[str] = "/icons/badge-72.png"
    data: Optional[dict] = None
    actions: Optional[list] = None
    tag: Optional[str] = None
    require_interaction: bool = True


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe(
    subscription: SubscriptionRequest,
    current_user: User = Depends(get_current_active_user),
):
    existing = await PushSubscription.find_one(
        PushSubscription.user_id == str(current_user.id),
        PushSubscription.endpoint == subscription.endpoint,
    )
    
    if existing:
        existing.active = True
        existing.keys = subscription.keys
        existing.user_agent = subscription.user_agent
        existing.last_used = datetime.utcnow()
        await existing.save()
        return SubscriptionResponse(
            id=str(existing.id),
            endpoint=existing.endpoint,
            active=existing.active,
            created_at=existing.created_at,
        )
    
    new_sub = PushSubscription(
        user_id=str(current_user.id),
        endpoint=subscription.endpoint,
        keys=subscription.keys,
        user_agent=subscription.user_agent,
    )
    await new_sub.insert()
    
    return SubscriptionResponse(
        id=str(new_sub.id),
        endpoint=new_sub.endpoint,
        active=new_sub.active,
        created_at=new_sub.created_at,
    )


@router.delete("/unsubscribe")
async def unsubscribe(
    endpoint: str,
    current_user: User = Depends(get_current_active_user),
):
    sub = await PushSubscription.find_one(
        PushSubscription.user_id == str(current_user.id),
        PushSubscription.endpoint == endpoint,
    )
    if sub:
        sub.active = False
        await sub.save()
    return {"success": True}


@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def list_subscriptions(
    current_user: User = Depends(get_current_active_user),
):
    subs = await PushSubscription.find(
        PushSubscription.user_id == str(current_user.id),
        PushSubscription.active == True,
    ).to_list()
    
    return [
        SubscriptionResponse(
            id=str(s.id),
            endpoint=s.endpoint,
            active=s.active,
            created_at=s.created_at,
        )
        for s in subs
    ]


@router.post("/send-test")
async def send_test_push(
    payload: PushPayload,
    current_user: User = Depends(get_current_active_user),
):
    if not settings.VAPID_PRIVATE_KEY or not settings.VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=500, detail="VAPID keys not configured")
    
    subs = await PushSubscription.find(
        PushSubscription.user_id == str(current_user.id),
        PushSubscription.active == True,
    ).to_list()
    
    if not subs:
        raise HTTPException(status_code=404, detail="No active subscriptions")
    
    vapid_claims = {"sub": settings.VAPID_CLAIMS_EMAIL}
    sent = 0
    failed = 0
    
    for sub in subs:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": sub.keys,
                },
                data=payload.model_dump_json(exclude_none=True),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims=vapid_claims,
            )
            sent += 1
            sub.last_used = datetime.utcnow()
            await sub.save()
        except WebPushException as e:
            failed += 1
            if e.response and e.response.status_code == 410:
                sub.active = False
                await sub.save()
    
    return {"sent": sent, "failed": failed}