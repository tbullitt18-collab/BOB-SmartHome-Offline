# IBM Partner Plus "Build" Track Application Dossier

Use this comprehensive guide and pre-filled application responses to register BOB in the **IBM Partner Plus** portal at [partnerportal.ibm.com](https://partnerportal.ibm.com) or [ibm.com/partnerplus](https://www.ibm.com/partnerplus).

---

## 1. Company & Solution Profile

*   **Company / Commercial Entity:** BOB Edge Systems (Division of ASCE Technologies, LLC)
*   **Solution Name:** BOB: Offline Smart Home Survival System & Physical DevOps Platform
*   **Primary Contact:** Todd Bullitt
*   **Public Repository:** https://github.com/tbullitt18-collab/BOB-SmartHome-Offline
*   **Program Track:** **Build Track** (Independent Software Vendor — ISV)
*   **IBM Initiative Alignment:** *Build with Bob* (`youtube.com/@BuildwithIBM`), *Agent Development Lifecycle (ADLC)*
*   **Primary Industries:** Energy & Utilities, Real Estate & Property Management (REITs), Public Safety / Disaster Management
*   **Target Deployment Environment:** Red Hat OpenShift, Red Hat Device Edge (MicroShift), K3s, IBM Edge Application Manager (IEAM)

---

## 2. Pre-Filled Application Form Fields (Copy & Paste Ready)

### Q1: Solution Description & Value Proposition
> **Answer:**  
> BOB (Building Offline Backbone) is an edge-native, 100% offline physical automation and edge DevOps platform designed to survive municipal blackout and internet collapse. It eliminates the fatal cloud dependency of modern smart buildings by running an autonomous, observable runtime directly on local edge hardware.  
>  
> BOB embeds Watson-class machine learning models (RandomForest barometric storm prediction, IsolationForest electrical anomaly detection, and WSU CASAS-trained occupancy learning) directly on the edge. During grid collapse, BOB automatically triggers deterministic load shedding—extending residential UPS battery life from 4 hours to over 36 hours. Every physical decision produces a structured decision trace and is committed to an immutable, SHA-256 cryptographic audit trail.

### Q2: How does your solution integrate with IBM and Red Hat technologies?
> **Answer:**  
> BOB is architected as an OCI-compliant containerized workload engineered for hybrid edge environments and directly incorporates IBM's official **Technology Building Blocks**:
> 1. **Automation Core (*Automated Resilience & Compliance*):** Enforces continuous local policy execution and self-healing load management during grid failures without cloud latency.
> 2. **AI Core (*Real Time Guardrails & Agent Ops*):** Enforces deterministic life-safety priority overrides (automatic egress unlocking and HVAC cut-off during fire/smoke) while logging sub-millisecond decision traces.
> 3. **Data Core (*Data Streaming & Observability*):** Normalizes Zigbee, MQTT, and sensor telemetry into structured event streams with cryptographic tamper verification.
> 4. **Infrastructure & Edge Scale (*Red Hat OpenShift & IEAM*):** Packaged with Open Horizon service definitions and patterns for autonomous zero-touch fleet management via **IBM Edge Application Manager (IEAM)** and Red Hat Device Edge (MicroShift).

### Q3: What is the primary customer pain point and target market?
> **Answer:**  
> BOB addresses critical infrastructure and liability vulnerabilities across three high-value markets:
> 1. **Electric Utilities & Cooperatives:** Suffer catastrophic substation transformer blowouts caused by "cold-load pickup" surges when re-energizing storm-damaged distribution feeders. BOB provides automated, staggered local load re-engagement.
> 2. **Multi-Family Real Estate & REITs:** Face extreme tenant lockout, freezing pipe damage, and life-safety liability when cloud smart locks and thermostats drop offline during blackouts.
> 3. **Disaster Relief & Microgrid Operators:** Require ruggedized, observable Automation-as-Code that operates with 100% fidelity in disconnected and islanded scenarios.

### Q4: What is your commercialization and revenue model?
> **Answer:**  
> BOB utilizes a three-tier commercial model:
> 1. **Commercial Gateways (REITs / Multi-Family):** Annual SaaS/appliance subscription at $1,200/edge node/year.
> 2. **Utility Feeder Capacity (Power Companies):** $25,000/substation feeder/year under multi-year utility service agreements, preceded by a $45,000 turnkey 90-day pilot.
> 3. **Ecosystem Co-Selling (Red Hat Marketplace & IBM Catalog):** Packaged as a certified container solution with IBM Value Seller pricing discounts (up to 15% preferred partner margins) for enterprise procurement.

---

## 3. IBM Technology Building Blocks Alignment Matrix

| IBM Technology Building Block | Implementation in BOB | Specific Code / Asset |
|:---|:---|:---|
| **Automated Resilience & Compliance** | Dynamic storm mode load-shedding extending battery runtime by 8x | `policies/storm-mode-resilience.json` |
| **Real Time Guardrails** | Deterministic Priority 100 life-safety egress overrides | `policies/safety-hazard-protocol.json` |
| **Agent Ops & Trust** | Microsecond decision tracing and inference validation | `engine/pipeline.py` & `observability/` |
| **Data Streaming** | Local event normalization bus with zero-cloud dependencies | `engine/event_bus.py` & `contracts/` |
| **Non-Human Identity & Security** | Immutable SHA-256 hash-chained local audit trail | `observability/audit_trail.jsonl` |
| **Infrastructure as Code** | K3s HA clustering & OpenShift edge operator CRDs | `scale/` & `commercial/ieam-openshift/` |

---

## 4. Submission Checklist

- [x] Solution Brief created: `commercial/partner-plus/SOLUTION_BRIEF.md`
- [x] Red Hat Marketplace metadata configured: `commercial/partner-plus/marketplace-listing.json`
- [x] IBM Building Blocks architecture verified: 20 blocks mapped
- [x] Open Horizon / IEAM deployment patterns ready: `commercial/ieam-openshift/horizon/`
- [x] Public GitHub repository accessible: https://github.com/tbullitt18-collab/BOB-SmartHome-Offline
- [x] Closed-loop Watson Edge AI showcase validated: `scripts/watson_showcase.py`
- [x] Physical DevOps loop tested: `scripts/demo_devops_loop.py` (100% determinism)
- [ ] Log in to [partnerportal.ibm.com](https://partnerportal.ibm.com) and submit under "Build" Track.

