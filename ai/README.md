# BOB Smart Home Offline AI Layer

This repository contains the Watson-class intelligence layer for BOB's Smart Home System.
It runs 100% locally and offline, without any dependency on cloud AI APIs.

## Features (Watson-class AI)

- **Storm & Outage Predictor** (`storm_predictor.py`): Uses Random Forest to analyze local weather telemetry (barometric pressure, temperature, wind) to predict grid outages before they happen.
- **Anomaly Detection** (`anomaly_detector.py`): Uses Isolation Forest models trained per-device to detect unusual power spikes, sensor drift, and unresponsive behavior.
- **Occupancy Learning** (`occupancy_learner.py`): Uses temporal probabilistic modeling to map daily routines and predict room occupancy, generating optimal time-windows for climate/lighting automation.
- **Device Health Monitoring** (`device_health_monitor.py`): Statistical analysis of device telemetry to predict impending hardware failures before they occur.
- **BOB Brain Orchestrator** (`bob_brain.py`): The core intelligence engine that synchronizes all AI models, generates Watson-style natural language summaries, and triggers proactive automations in Home Assistant.

## Installation

Ensure you have Python 3.9+ installed.

```bash
pip install -r requirements.txt
```

## Running the Brain

Run the central intelligence node:

```bash
python bob_brain.py
```

To run individual modules for testing/demo purposes, execute them directly:

```bash
python storm_predictor.py
python anomaly_detector.py
python occupancy_learner.py
python device_health_monitor.py
```

## Integration with Home Assistant

BOB's Brain is designed to integrate directly with Home Assistant via the REST API or MQTT. It ingests sensor data in real-time, runs local inference cycles, and triggers HA scripts/automations autonomously based on predictive insights.
