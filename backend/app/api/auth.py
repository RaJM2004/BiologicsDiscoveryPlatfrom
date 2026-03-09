from fastapi import APIRouter, HTTPException, Depends, status
from app.models.user import User
from app.models.activity import UserActivity
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import json
import hmac
import hashlib
import base64
import time
from datetime import datetime

router = APIRouter()

SECRET_KEY = "super-secret-key-change-this"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None
    is_superuser: bool = False # Allow creating admin for demo

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str = None
    is_active: bool
    is_superuser: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    role: str

def create_token(user_id: str, role: str):
    payload = {
        "sub": user_id,
        "role": role,
        "exp": time.time() + 3600 * 24  # 1 day
    }
    payload_str = json.dumps(payload)
    signature = hmac.new(SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{payload_str}.{signature}".encode()).decode()
    return token

def verify_token(token: str):
    try:
        decoded = base64.urlsafe_b64decode(token).decode()
        payload_str, signature = decoded.split(".")
        expected_sig = hmac.new(SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        if signature != expected_sig:
            return None
        payload = json.loads(payload_str)
        if payload["exp"] < time.time():
            return None
        return payload
    except Exception:
        return None

from app.api.dependencies import get_current_active_superuser, get_current_user

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    existing_user = await User.find_one(User.email == user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Store plain for MVP demo (in real app use bcrypt)
    hashed_fake = f"hashed_{user.password}" 
    
    # Auto-promote specific admin email
    is_admin = user.is_superuser
    if user.email == "admin@genesysquantis.com":
        is_admin = True

    new_user = User(
        email=user.email, 
        hashed_password=hashed_fake, 
        full_name=user.full_name,
        is_superuser=is_admin
    )
    await new_user.insert()
    
    # Log activity
    await UserActivity(
        user_id=str(new_user.id), 
        user_email=new_user.email,
        action="REGISTER",
        details={"email": user.email}
    ).insert()
    
    return UserResponse(
        id=str(new_user.id), 
        email=new_user.email, 
        full_name=new_user.full_name, 
        is_active=new_user.is_active,
        is_superuser=new_user.is_superuser
    )

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    user = await User.find_one(User.email == user_in.email)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Verify fake hash
    if user.hashed_password != f"hashed_{user_in.password}":
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    role = "admin" if user.is_superuser else "user"
    token = create_token(str(user.id), role)
    
    # Log activity
    await UserActivity(
        user_id=str(user.id), 
        user_email=user.email,
        action="LOGIN",
        details={"role": role}
    ).insert()

    return Token(access_token=token, token_type="bearer", user_id=str(user.id), role=role)

@router.get("/users", response_model=List[UserResponse])
async def get_users():
    users = await User.find_all().to_list()
    return [
        UserResponse(
            id=str(u.id), 
            email=u.email, 
            full_name=u.full_name, 
            is_active=u.is_active,
            is_superuser=u.is_superuser
        ) for u in users
    ]

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser
    )
