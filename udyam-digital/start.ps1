# -----------------------------------------------------------------------------
# start.ps1 - One-click startup for Udyam Digital
# Run from the udyam-digital folder
# -----------------------------------------------------------------------------

Write-Host "=== Udyam Digital - Accel Business ===" -ForegroundColor Cyan
Write-Host ""

$backendDir = Join-Path $PSScriptRoot "backend"
$frontendDir = Join-Path $PSScriptRoot "frontend"
$envFile = Join-Path $backendDir ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "[ERROR] backend\.env not found. Copy backend\.env.example to backend\.env and add your GOOGLE_API_KEY." -ForegroundColor Red
    exit 1
}

$envContent = Get-Content $envFile -Raw
if ($envContent -match "your_google_api_key_here") {
    Write-Host "[WARNING] GOOGLE_API_KEY is not set in backend\.env" -ForegroundColor Yellow
    Write-Host "  The advisor (Digi Saathi) will not work without it." -ForegroundColor Yellow
    Write-Host "  Get a free key at: https://aistudio.google.com/app/apikey" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "[1/2] Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Green
Start-Process cmd.exe -WorkingDirectory $backendDir -ArgumentList "/k", "venv\Scripts\uvicorn main:app --reload --port 8000"

Write-Host "      Waiting 6 seconds for backend to initialise..." -ForegroundColor DarkGray
Start-Sleep -Seconds 6

Write-Host "[2/2] Starting React dev server on http://localhost:3000 ..." -ForegroundColor Green
Start-Process cmd.exe -WorkingDirectory $frontendDir -ArgumentList "/k", "npm run dev"

Write-Host ""
Write-Host "=== Both servers starting! ===" -ForegroundColor Cyan
Write-Host "  Backend API:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend App: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Close the spawned command windows to stop the servers." -ForegroundColor DarkGray
