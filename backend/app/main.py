import os
import webbrowser
import threading
import time
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Biologics Discovery Platform API",
    description="Backend API for AI-assisted biologics discovery, screening, and validation.",
    version="0.1.0"
)

# CORS Configuration
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000", 
    "http://localhost:8080", 
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")

# Mount Static Files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

def open_browser():
    """Opens the browser to the landing page after a short delay."""
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000")
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
    
    # Automatically open browser if not disabled
    if os.environ.get("AUTO_OPEN_BROWSER", "true").lower() == "true":
        # Only open if this is the main worker (not the reloader process window)
        # Uvicorn reload works by starting a main process and then a worker process.
        # This will still trigger on reloads, which is what the user asked for.
        threading.Thread(target=open_browser, daemon=True).start()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the landing page."""
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/{page}.html", response_class=HTMLResponse)
async def serve_html_page(request: Request, page: str):
    """Serve other HTML templates by name."""
    try:
        return templates.TemplateResponse(f"{page}.html", {"request": request})
    except Exception:
        return HTMLResponse(content="Page not found", status_code=404)

@app.get("/api/status")
def read_root_api():
    return {"message": "Biologics Discovery Platform API is running", "version": "0.1.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

from app.api import auth, targets, screening, experiments, optimization, admin, docking, admet, robot, chatbot, reports, monitoring, preformulation, formulation, pockets

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
app.include_router(preformulation.router, prefix="/api/preformulation", tags=["Preformulation"])
app.include_router(formulation.router, prefix="/api/formulation", tags=["Formulation"])
app.include_router(pockets.router, prefix="/api/pockets", tags=["Pockets"])

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

