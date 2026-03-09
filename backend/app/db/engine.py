from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models import User, Target, Experiment, ScreeningJob, OptimizationJob, UserActivity

async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=[User, Target, Experiment, ScreeningJob, OptimizationJob, UserActivity])
    print(f"Connected to MongoDB at {settings.MONGODB_URL}")
