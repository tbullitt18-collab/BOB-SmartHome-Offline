# BOB: Smart Home Offline Edge AI
*A resilient, offline-first smart home control system built for the IBM Bob Challenge Hackathon.*

## THE PROBLEM
Modern smart homes rely heavily on cloud infrastructure. When the internet goes down or during a storm, your smart home becomes a collection of dumb bricks. You lose control of your lights, security, and climate just when you need them most.

## THE SOLUTION
Meet **BOB** – a local, embedded Edge AI that survives offline. By bringing IBM Watson-class intelligence to the edge, BOB ensures your home remains smart, secure, and responsive, completely independent of cloud connectivity. It acts as an autonomous nervous system for your home, prioritizing critical infrastructure and adapting to changing conditions even in a blackout.

## HOW TO OPERATE
To get BOB up and running, follow these steps:
1. **Boot the Dashboard:** Start the local web server to access the smart home dashboard at `http://localhost:8080`.
2. **Run the AI:** Launch the BOB AI engine to begin processing local sensor data and making autonomous decisions.
3. **Storm Mode:** During severe weather or internet outages, BOB automatically enters "Storm Mode," switching to local processing and conserving power. You can also manually trigger this from the dashboard.

## FEATURES
- **Watson-Class AI Modules:** 4 integrated AI models for predictive climate control, anomaly detection, energy optimization, and local natural language processing.
- **Graphite Metrics:** Real-time, granular telemetry and monitoring of all smart home devices, powered by Graphite.
- **K3s Enterprise Scaling:** Lightweight Kubernetes (K3s) ensures high availability and allows the system to scale effortlessly from a single Raspberry Pi to a cluster of edge nodes.
