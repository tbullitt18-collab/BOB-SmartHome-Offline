# BOB: Offline Smart Home Survival System & Physical Automation DevOps Platform

> **An Edge-Native, 100% Offline Smart Home Platform that bridges developer workflow pains with resilient physical automation—surviving power blackouts and internet collapse.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Edge AI](https://img.shields.io/badge/Edge%20AI-Watson--Class-blue.svg)](ai/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready%20POC-brightgreen.svg)](scripts/)
[![DevOps Loop](https://img.shields.io/badge/Physical%20DevOps-Observable%20%26%20Replayable-orange.svg)](DEVELOPER_WORKFLOWS.md)

---

## ⚠️ The Problem
1. **Cloud & ISP Fragility:** Modern smart homes turn into unresponsive bricks when severe storms cut municipal power and cloud internet. Homeowners are locked out of digital locks, lose security cameras, and drain battery backups within hours.
2. **Developer Workflow Gaps:** Smart home systems lack engineering rigor—zero test environments, invisible decision logic, unversioned automation rules, and no audit trails when physical devices fail.

## 💡 The Solution
**BOB** transforms the home into a **local, observable edge runtime**:
- **100% Offline Control:** Operates on local Zigbee/Z-Wave mesh networks and a lightweight Python stdlib API bridge with zero external CDN dependencies.
- **Watson-Class Edge AI:** Runs embedded Scikit-learn `RandomForestClassifier` (storm prediction) and `IsolationForest` (power anomaly detection) directly on edge hardware.
- **Real-World CASAS Dataset Modeling:** Dynamic load-shedding based on millions of rows from the WSU CASAS dataset, stretching UPS battery life from 4 hours to over 36 hours.
- **Physical Automation DevOps Platform:** Automation-as-Code (`policies/`), strict event contracts (`contracts/`), deterministic event replay (`simulator/`), and SHA-256 hash-chained audit trails (`observability/`).

---

## 📁 Repository Architecture

```text
BOB-SmartHome-Offline/
├── contracts/               # JSON schemas for events, capabilities & policies
├── policies/                # Versioned Automation-as-Code policies (Safety, Storm, Focus, Energy)
├── observability/           # Structured Decision Traces & SHA-256 Cryptographic Audit Log
├── engine/                  # Core Event Bus & Policy Pipeline Orchestrator
├── simulator/               # Device Emulator, Event Replay Engine & Chaos Fault Injector
├── ai/                      # Watson-class Edge ML (StormPredictor, AnomalyDetector, OccupancyLearner)
├── dashboard/               # Zero-CDN Dark-Mode LAN Command Center (Port 8888)
├── deploy/                  # Environment profiles (Dev, Staging, Production)
├── scale/                   # Enterprise K3s HA, Clustered EMQX MQTT & Nginx
├── hub/                     # Home Assistant local configuration templates
├── docs/                    # HD Video Demonstration (Docs & Media) & Screenshots
└── scripts/                 # Launcher scripts & DevOps Loop verification
```

---

## 🚀 Quickstart & Verification

### 1. Run the Automation DevOps Loop (End-to-End Test)
Verifies event normalization, deterministic policy evaluation, AI inference, structured decision tracing, cryptographic audit logging, and CI/CD event replay:
```bash
python scripts/demo_devops_loop.py
```

### 2. Launch the Offline Command Center
Starts the local LAN dashboard and API bridge on `http://localhost:8888`:
```powershell
.\scripts\launch_bob.ps1
```

### 3. Run the Watson AI Edge Showcase
Executes the closed-loop edge machine learning models:
```bash
python scripts/watson_showcase.py
```

### 4. Ingest Academic-Grade CASAS Datasets
Stream millions of rows from real-world smart home datasets into BOB's `OccupancyLearner`:
```bash
python scripts/analyze_casas.py path/to/casas_data.txt --sensor M003
```

---

## 📖 Extended Documentation
- [**Developer Workflows & Physical DevOps Guide**](DEVELOPER_WORKFLOWS.md): Detailed deep-dive into event schemas, decision traces, and CI/CD replay.
- [**Enterprise Scaling Architecture**](scale/ENTERPRISE_SCALING_GUIDE.md): K3s Kubernetes clustering and EMQX multi-broker scaling.
- [**IBM Bob Utilization Statement**](IBM_Bob_Utilization_Statement.md): Official statement on how IBM Bob was utilized to generate code syntax.
- [**Visual Architecture & Session Evidence**](docs/screenshots/README.md): High-resolution screenshots and session logs.

---

## 🏆 Hackathon Deliverables
- **Demo Video (Cloned Voice Narration):** [`docs/BOB_Hackathon_Demo_Video.mp4`](docs/BOB_Hackathon_Demo_Video.mp4)
- **Session Telemetry:** [`IBM_Bob_Session_Report.jsonl`](IBM_Bob_Session_Report.jsonl)
- **Compliance Statement:** [`IBM_Bob_Utilization_Statement.md`](IBM_Bob_Utilization_Statement.md)
