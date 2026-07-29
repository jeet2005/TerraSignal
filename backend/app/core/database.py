from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models import User, Event, CompoundEvent, PushSubscription


async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    await init_beanie(
        database=db,
        document_models=[User, Event, CompoundEvent, PushSubscription],
    )
    
    return client


async def close_db(client: AsyncIOMotorClient):
    client.close()