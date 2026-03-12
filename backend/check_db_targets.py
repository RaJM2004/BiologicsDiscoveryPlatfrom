import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load connection string
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://quantxai25_db_user:2Xj4kePUqLqoIZcm@cluster0.qyzjacn.mongodb.net/?appName=Cluster0")

async def check():
    from app.models.target import Target
    client = AsyncIOMotorClient(MONGO_URI)
    db = client['test']
    await init_beanie(database=db, document_models=[Target])
    
    targets = await Target.find_all().to_list()
    print("Available Targets in DB:")
    for t in targets:
        print(f"- {t.name} (PDB IDs: {t.pdb_ids})")

if __name__ == "__main__":
    asyncio.run(check())
