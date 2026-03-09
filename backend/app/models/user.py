from typing import Optional
from beanie import Document
from pydantic import EmailStr
from datetime import datetime

class User(Document):
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = datetime.now()

    class Settings:
        name = "users"
