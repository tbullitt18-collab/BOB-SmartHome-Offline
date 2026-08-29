$ErrorActionPreference = 'Stop'

function Show-Banner {
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "   ____  ____  ____    ____  _   _  ____ " -ForegroundColor Cyan
    Write-Host "  | __ )/ __ \| __ )  / ___|| | | |/ ___|" -ForegroundColor Cyan
    Write-Host "  |  _ \ |  | |  _ \  \___ \| |_| | |  _ " -ForegroundColor Cyan
    Write-Host "  | |_) | |__| | |_) |  ___) |  _  | |_| |" -ForegroundColor Cyan
    Write-Host "  |____/ \____/|____/  |____/|_| |_|\____|" -ForegroundColor Cyan
    Write-Host "                                         " -ForegroundColor Cyan
    Write-Host "  SMART HOME COMMAND CENTER - HACKATHON ED" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
}

Show-Banner

Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# Check Docker (informational, not failing if absent per offline requirement)
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Docker is running." -ForegroundColor Green
    } else {
        Write-Host "[WARN] Docker is not running. Metrics stack will be disabled." -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "[WARN] Docker is not installed. Metrics stack will be disabled." -ForegroundColor DarkYellow
}

$dashboardDir = Join-Path $PSScriptRoot "..\dashboard"
$apiScript = Join-Path $dashboardDir "api_bridge.py"

Write-Host "Starting API Bridge..." -ForegroundColor Yellow
$apiJob = Start-Job -ScriptBlock {
    param($scriptPath)
    python $scriptPath
} -ArgumentList $apiScript

Start-Sleep -Seconds 2

if ($apiJob.State -eq 'Running') {
    Write-Host "[OK] API Bridge running on port 8888" -ForegroundColor Green
} else {
    Write-Host "[FAIL] API Bridge failed to start." -ForegroundColor Red
    Receive-Job $apiJob
    exit 1
}

Write-Host "Opening Dashboard in default browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8888"

while ($true) {
    Write-Host "`n--- MENU ---"
    Write-Host "[1] Open Dashboard"
    Write-Host "[2] View Logs"
    Write-Host "[3] Run AI Analysis"
    Write-Host "[4] Check Network"
    Write-Host "[5] Stop All and Exit"
    $choice = Read-Host "Select an option"

    switch ($choice) {
        '1' { Start-Process "http://localhost:8888" }
        '2' { 
            Write-Host "Recent Logs:" -ForegroundColor Cyan
            Receive-Job $apiJob -Keep 
        }
        '3' { Write-Host "Running local AI models... (Simulated) -> All systems normal." -ForegroundColor Green }
        '4' { Test-NetConnection localhost -Port 8888 }
        '5' { 
            Write-Host "Stopping services..." -ForegroundColor Yellow
            Stop-Job $apiJob
            Remove-Job $apiJob
            Write-Host "Goodbye!" -ForegroundColor Green
            exit 0
        }
        default { Write-Host "Invalid option." -ForegroundColor Red }
    }
}
