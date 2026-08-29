$logFile = "C:\Users\tbull\.gemini\antigravity\scratch\BOB-SmartHome-Offline\scripts\network_health.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Check-Ping {
    param ($address, $name)
    $result = Test-Connection -ComputerName $address -Count 1 -Quiet -ErrorAction SilentlyContinue
    if ($result) {
        Write-Host "$name ($address) is UP" -ForegroundColor Green
        return "$name ($address) is UP"
    } else {
        Write-Host "$name ($address) is DOWN" -ForegroundColor Red
        return "$name ($address) is DOWN"
    }
}

Write-Host "--- Network Health Check ---" -ForegroundColor Cyan
$results = @()

$results += Check-Ping -address "8.8.8.8" -name "ISP Internet"
$results += Check-Ping -address "192.168.1.10" -name "Local Hub (HA)"
$results += Check-Ping -address "192.168.1.1" -name "Local Router"

$logEntry = "[$timestamp]`n" + ($results -join "`n") + "`n"
Add-Content -Path $logFile -Value $logEntry
Write-Host "Results logged to $logFile" -ForegroundColor Yellow
