# TerraRisk Workshop - Development Script
# Run both backend and frontend for local development

Write-Host "Starting TerraRisk Workshop Development Environment" -ForegroundColor Green

# Kill existing processes on ports 3000 and 8000
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Start backend in new window
Write-Host "Starting Backend (FastAPI)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\backend'; python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Write-Host "Starting Frontend (Next.js)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\frontend'; npm run dev"

Write-Host ""
Write-Host "Development servers starting:" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Admin:    http://localhost:3000/admin" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop." -ForegroundColor Gray
