import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.user import User
from app.models.activity import UserActivity

async def debug_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=[User, UserActivity])
    
    users = await User.find_all().to_list()
    if not users:
        print("No users found.")
        return

    target_user = users[0]
    target_id_str = str(target_user.id)
    
    print(f"Target User: {target_user.email}")
    print(f"Target User ID (raw): {target_user.id} (type: {type(target_user.id)})")
    print(f"Target User ID (str): '{target_id_str}'")
    
    # Simulate Query
    print(f"Querying UserActivity where user_id == '{target_id_str}'...")
    activities = await UserActivity.find(UserActivity.user_id == target_id_str).to_list()
    
    print(f"Found {len(activities)} activities.")
    for a in activities:
        print(f" - {a.action} (stored user_id: '{a.user_id}')")
        
    # Check if ANY activities exist
    all_activities = await UserActivity.find_all().to_list()
    print(f"\nTotal Activities in DB: {len(all_activities)}")
    if all_activities:
        sample = all_activities[0]
        print(f"Sample activity user_id: '{sample.user_id}' (type: {type(sample.user_id)})")
        print(f"Match check: '{sample.user_id}' == '{target_id_str}' -> {sample.user_id == target_id_str}")

if __name__ == "__main__":
    asyncio.run(debug_db())
