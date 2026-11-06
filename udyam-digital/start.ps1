# ─────────────────────────────────────────────────────────────────────────────
# start.ps1  —  One-click startup for Udyam Digital
# Run from the udyam-digital\ folder
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "=== Udyam Digital — Accel Business ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check .env exists and has API key
$envFile = Join-Path $PSScriptRoot "backend\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "[ERROR] backend\.env not found. Copy backend\.env.example → backend\.env and add your GOOGLE_API_KEY." -ForegroundColor Red
    exit 1
}
$envContent = Get-Content $envFile -Raw
if ($envContent -match "your_google_api_key_here") {
    Write-Host "[WARNING] GOOGLE_API_KEY is not set in backend\.env" -ForegroundColor Yellow
    Write-Host "  The advisor (Digi Saathi) will not work without it." -ForegroundColor Yellow
    Write-Host "  Get a free key at: https://aistudio.google.com/app/apikey" -ForegroundColor Yellow
    Write-Host ""
}

# 2. Start backend in a new window
Write-Host "[1/2] Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Green
$backendCmd = "Set-Location '$PSScriptRoot\backend'; .\venv\Scripts\uvicorn main:app --reload --port 8000; Read-Host 'Press Enter to close'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# 3. Wait for backend to warm up (model training takes ~5 seconds)
Write-Host "      Waiting 7 seconds for backend to initialise propensity model..." -ForegroundColor DarkGray
Start-Sleep 7

# 4. Start frontend in a new window
Write-Host "[2/2] Starting React dev server on http://localhost:5173 ..." -ForegroundColor Green
$frontendCmd = "Set-Location '$PSScriptRoot\frontend'; npm run dev; Read-Host 'Press Enter to close'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host ""
Write-Host "=== Both servers starting... ===" -ForegroundColor Cyan
Write-Host "  Backend API:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend App: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each terminal to stop the servers." -ForegroundColor DarkGray

