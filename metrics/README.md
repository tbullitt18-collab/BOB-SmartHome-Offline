# BOB's Smart Home Offline System - Metrics Stack

This directory contains the core monitoring and observability stack for the BOB Smart Home System. It is designed to operate completely offline (no internet required), ensuring local metrics collection, long-term storage, and visualizations are always available.

## Components

- **Graphite & Carbon**: A time-series database (TSDB) stack that efficiently stores metrics over time. Carbon receives the metrics via its plaintext protocol, and Graphite provides the query API.
- **Grafana**: A visualization web application that connects to Graphite to display beautiful and functional dashboards.

## Getting Started

To spin up the entire metrics stack, simply use Docker Compose:

```bash
docker-compose up -d
```

### Accessing the Interfaces

- **Grafana (Dashboards)**: [http://localhost:3000](http://localhost:3000) (Login: admin/admin)
- **Graphite Web UI (Raw data)**: [http://localhost:8080](http://localhost:8080)
- **Carbon (Metrics Receiver)**: `localhost:2003`

## Metric Naming Convention

Metrics should be sent to Carbon over TCP port 2003 in the plaintext format: `<metric_path> <value> <timestamp>\n`.

We use a structured namespace for all smart home metrics:
- `smart_home.devices.<device_name>.status` (0 = offline, 1 = online)
- `smart_home.power.<device_name>.watts`
- `smart_home.network.<device_name>.<metric>` (e.g., ping)
- `smart_home.sensors.<room_name>.<sensor_type>` (e.g., temperature, motion)
- `smart_home.battery.<device_name>.level` (0-100%)

Example: `smart_home.devices.living_room.light.status 1 1693310000`

## Data Retention (Storage Schemas)

Data is rolled up over time to save disk space while preserving long-term trends, controlled by `carbon/storage-schemas.conf`:
- Devices: 10s for 1d, 1m for 7d, 5m for 30d, 1h for 2y
- Power: 10s for 7d, 1m for 30d, 1h for 2y
- Network: 30s for 7d, 5m for 90d
- Sensors: 30s for 3d, 5m for 30d, 1h for 1y
- Battery: 1m for 30d, 1h for 2y

## Offline Operation

Since this stack is fully self-hosted on the local network hub, all dashboards, metric retention, and rendering are performed locally. As long as your local area network (LAN) is functional, the monitoring stack will remain 100% operational, regardless of ISP connectivity.
