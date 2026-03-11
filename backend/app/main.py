from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Biologics Discovery Platform API",
    description="Backend API for AI-assisted biologics discovery, screening, and validation.",
    version="0.1.0"
)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:8080", 
    "*" # Adjust for production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (if serving frontend from FastAPI for simple MVP)
# In production, Nginx or similar should handle this, or a separate frontend server.
# For this MVP, we will assume frontend is served separately or via templates.
from app.db.engine import init_db
from app.api import auth, targets, screening, experiments, optimization, admin, docking, admet, chatbot

@app.on_event("startup")
async def start_db():
    await init_db()
    
    # Init Admin
    from app.models.user import User
    email = "admin@genesysquantis.com"
    existing = await User.find_one(User.email == email)
    if not existing:
        print(f"Creating default admin: {email}")
        await User(
            email=email,
            hashed_password=f"hashed_admin", # Matches auth.py logic
            full_name="System Admin",
            is_superuser=True,
            is_active=True
        ).insert()
    elif not existing.is_superuser:
        print(f"Promoting {email} to admin")
        existing.is_superuser = True
        await existing.save()

@app.get("/")
def read_root():
    return {"message": "Biologics Discovery Platform API is running", "version": "0.1.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

from app.api import auth, targets, screening, experiments, optimization, admin, docking, admet, robot, chatbot, reports, monitoring

# ... existing code ...

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(targets.router, prefix="/api/targets", tags=["Targets"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["Experiments"])
app.include_router(screening.router, prefix="/api/screening", tags=["Screening"])
app.include_router(optimization.router, prefix="/api/optimization", tags=["Optimization"])
app.include_router(docking.router, prefix="/api/docking", tags=["Docking"])
app.include_router(admet.router, prefix="/api/admet", tags=["ADMET"])
app.include_router(robot.router, prefix="/api/robot", tags=["Robot"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(chatbot.router, prefix="/api/chat", tags=["Chatbot"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])

from fastapi import WebSocket, WebSocketDisconnect
from app.utils.websockets import manager

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)
    try:
        while True:
            await websocket.receive_text() # Keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)

