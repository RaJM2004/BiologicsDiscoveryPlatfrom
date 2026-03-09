@echo off
SETLOCAL EnableExtensions EnableDelayedExpansion

echo ==========================================
echo 🧬 Biologics Discovery Platform Setup
echo ==========================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

echo [INFO] Python found.

REM --- BACKEND SETUP ---
echo.
echo [1/4] Setting up Backend...
cd backend

IF NOT EXIST "venv" (
    echo    - Creating virtual environment...
    python -m venv venv
) ELSE (
    echo    - Virtual environment exists.
)

echo    - Activating virtual environment...
call venv\Scripts\activate

echo    - Installing dependencies (this might take a few minutes)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM --- START SERVERS ---
echo.
echo [2/4] Starting Backend Server...
echo    - Launching Uvicorn in a new window...
start "Biologics Backend" cmd /k "venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM --- FRONTEND ---
echo.
echo [3/4] Launching Frontend...
cd ..\frontend\templates
start login.html

echo.
echo [4/4] Done! 
echo.
echo - Backend API Docs: http://127.0.0.1:8000/docs
echo - Frontend: Opened in your default browser.
echo.
echo Keep this window open or close it to exit the setup script (backend will keep running).
pause
