import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Biologics Discovery Platform"
    API_V1_STR: str = "/api/v1"
    
    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb+srv://<db_username>:<db_password>@cluster0.qyzjacn.mongodb.net/?appName=Cluster0")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "biologics_platform")

    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
