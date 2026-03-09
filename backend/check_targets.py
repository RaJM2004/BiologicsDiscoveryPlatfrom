import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import List, Optional
from datetime import datetime
from beanie import Document
from pydantic import BaseModel

class TargetProperties(BaseModel):
    molecular_weight: Optional[float] = None
    solubility: Optional[str] = None
    affinity: Optional[float] = None

class Target(Document):
    name: str
    type: str
    sequence: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[TargetProperties] = None
    status: str = "Candidate"
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "targets"

async def check_db():
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")
    database_name = os.getenv("DATABASE_NAME", "biologics_platform")
    
    print(f"Connecting to: {mongodb_url}")
    print(f"Database: {database_name}")
    
    client = AsyncIOMotorClient(mongodb_url)
    await init_beanie(database=client[database_name], document_models=[Target])
    
    count = await Target.count()
    print(f"Total Targets: {count}")
    targets = await Target.find_all().to_list()
    for t in targets:
        print(f"- {t.name} ({t.type}) | ID: {t.id}")

if __name__ == "__main__":
    asyncio.run(check_db())
