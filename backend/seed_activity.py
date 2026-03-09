import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.user import User
from app.models.activity import UserActivity

async def seed_activity():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=[User, UserActivity])
    
    users = await User.find_all().to_list()
    print(f"Found {len(users)} users. Seeding activity for all...")
    
    for user in users:
        print(f"Seeding for {user.email}...")
        log = UserActivity(
            user_id=str(user.id),
            user_email=user.email,
            action="SYSTEM_CHECK",
            details={"note": "Verifying admin panel display"}
        )
        await log.insert()
        print(f" - Log inserted for {user.email}")

if __name__ == "__main__":
    asyncio.run(seed_activity())
