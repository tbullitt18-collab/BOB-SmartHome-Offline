# BOB Smart Home Command Center

The ultimate offline-first smart home dashboard built for speed, reliability, and security.

## Features
- **Offline First:** Zero external dependencies, no CDNs, no cloud telemetry.
- **Hackathon Quality UI:** Custom CSS dark theme with real-time animated indicators.
- **System Status:** Monitor hub uptime, local network, and UPS battery.
- **Storm Mode:** One-click emergency lockdown mode.
- **Device Control:** Fast toggles for lights, locks, and climate.
- **AI Insights:** Local edge-computed insights (simulated in UI).

## Screenshots / What You'll See
The dashboard features a high-contrast dark theme with a grid layout. 
- Top header with live clock and glowing network status.
- Left column: System Status and Storm Alert Panel.
- Middle column: Device Controls (Lights, Locks, Climate).
- Right column: Power Monitor, AI Insights, and Quick Actions.

## How to Launch
Run the included PowerShell script to start the backend and open the UI:
```powershell
.\scripts\launch_bob.ps1
```

## Offline Access
The dashboard is accessible locally at:
http://localhost:8888

To access it from your phone on the same network, find your computer's IP address (e.g., `192.168.1.100`) and visit:
http://192.168.1.100:8888

## How AI Insights Get Data
In this offline-first architecture, the "BOB Brain" AI runs locally on the hub. It ingests the JSON state from the `api_bridge.py` metrics endpoint and generates a local report, surfaced via the `/api/ai/report` endpoint. (Note: Currently simulated in the UI for demonstration).

## Keyboard Shortcuts
- `S` - Toggle Storm Mode (Locks everything, turns UI red/orange)
- `L` - Secure all locks instantly
