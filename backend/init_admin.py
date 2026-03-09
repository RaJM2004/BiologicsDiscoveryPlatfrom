import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.db.engine import init_db
import os

# Mock settings if needed or just hardcode for script
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "bio_platform"

async def init():
    # Connect
    client = AsyncIOMotorClient(MONGODB_URL)
    await init_beanie(database=client[DATABASE_NAME], document_models=[User])
    
    email = "admin@genesysquantis.com"
    password = "admin" # Default password
    hashed_fake = f"hashed_{password}"
    
    # Check if exists
    existing = await User.find_one(User.email == email)
    if existing:
        print(f"Admin user {email} already exists.")
        if not existing.is_superuser:
            print("Promoting to superuser...")
            existing.is_superuser = True
            await existing.save()
            print("Done.")
    else:
        print(f"Creating admin user {email}...")
        admin = User(
            email=email,
            hashed_password=hashed_fake,
            full_name="System Admin",
            is_superuser=True,
            is_active=True
        )
        await admin.insert()
        print(f"Admin created. Password: {password}")

if __name__ == "__main__":
    asyncio.run(init())
