Write-Host "Setting up Home Assistant local access..." -ForegroundColor Cyan

$hostsPath = "$env:windir\System32\drivers\etc\hosts"
$haEntry = "192.168.1.10 homeassistant.local"

# 1. Add static DNS entry
Write-Host "Checking hosts file for homeassistant.local..."
if ((Get-Content $hostsPath -ErrorAction SilentlyContinue) -match "homeassistant.local") {
    Write-Host "Hosts entry already exists." -ForegroundColor Yellow
} else {
    Write-Host "Adding hosts entry..." -ForegroundColor Green
    # Require admin for actual write, simulated here if no admin
    try {
        Add-Content -Path $hostsPath -Value "`n$haEntry" -ErrorAction Stop
        Write-Host "Hosts entry added successfully." -ForegroundColor Green
    } catch {
        Write-Host "Could not write to hosts file. Run as Administrator." -ForegroundColor Red
    }
}

# 2. Check if HA is reachable
Write-Host "Checking if HA is reachable at 192.168.1.10:8123..."
$haReachable = $false
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.ConnectAsync("192.168.1.10", 8123).Wait(1000)
    if ($tcp.Connected) {
        $haReachable = $true
        $tcp.Close()
    }
} catch {
    # Ignore
}

if ($haReachable) {
    Write-Host "Home Assistant is REACHABLE!" -ForegroundColor Green
    
    # 3. Open dashboard
    Write-Host "Opening HA Dashboard in default browser..."
    Start-Process "http://192.168.1.10:8123"
} else {
    Write-Host "Home Assistant is UNREACHABLE! Please check the hub." -ForegroundColor Red
}

# 4. Add Firewall Rule
Write-Host "Adding Windows Firewall rule for HA Local Traffic..."
try {
    New-NetFirewallRule -DisplayName "Allow HA Local Network" -Direction Inbound -LocalPort 8123 -Protocol TCP -Action Allow -RemoteAddress "192.168.1.0/24" -ErrorAction Stop | Out-Null
    Write-Host "Firewall rule added." -ForegroundColor Green
} catch {
    Write-Host "Could not add firewall rule. Run as Administrator." -ForegroundColor Red
}

Write-Host "Setup complete." -ForegroundColor Cyan
