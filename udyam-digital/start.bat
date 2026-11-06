@echo off
echo === Udyam Digital — Accel Business ===
echo.

REM Check .env exists
if not exist "backend\.env" (
    echo [ERROR] backend\.env not found.
    echo Copy backend\.env.example to backend\.env and add your GOOGLE_API_KEY.
    pause
    exit /b 1
)

echo [1/2] Starting FastAPI backend on http://localhost:8000 ...
start "Udyam-Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\uvicorn main:app --reload --port 8000"

echo Waiting 7 seconds for backend to warm up...
timeout /t 7 /nobreak >nul

echo [2/2] Starting React frontend on http://localhost:5173 ...
start "Udyam-Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo === Both servers starting! ===
echo   Backend API docs: http://localhost:8000/docs
echo   Frontend App:     http://localhost:5173
echo.
pause

