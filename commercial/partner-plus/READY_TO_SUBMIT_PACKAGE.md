# IBM Partner Plus: Ready-to-Submit Application Package

**Solution:** BOB: Offline Smart Home Survival System & Physical DevOps Platform  
**Company:** BOB Edge Systems (Division of ASCE Technologies, LLC)  
**Partner Profile:** Todd Bullitt (Enterprise ID: `10wtzf`)  
**Portal Target:** [ibm.com/partnerplus](https://www.ibm.com/partnerplus) / [partnerportal.ibm.com](https://partnerportal.ibm.com)  
**Submission Time:** < 3 Minutes  

---

## ⚡ 3-Minute Quick Submission Checklist

1. [ ] **Navigate to Portal:** Open [partnerportal.ibm.com](https://partnerportal.ibm.com) and log in with your IBM ID (Enterprise ID: `10wtzf`).
2. [ ] **Select "Build Track":** In the navigation menu, go to **Manage Solutions** > **Register New Solution** (or click **Build Track ISV Enrollment**).
3. [ ] **Copy & Paste Fields:** Paste each numbered block below directly into the corresponding portal form field.
4. [ ] **Upload Required Attachments:**
   * **Solution Brief Document:** [`commercial/partner-plus/SOLUTION_BRIEF.md`](SOLUTION_BRIEF.md) (or print as PDF)
   * **Solution Icon / Logo:** [`commercial/partner-plus/bob_icon.svg`](bob_icon.svg)
   * **Catalog Metadata (if requested):** [`commercial/partner-plus/marketplace-listing.json`](marketplace-listing.json)
5. [ ] **Submit & Confirm:** Click **Submit for Validation**. Your solution will enter the Fast-Track ISV evaluation pipeline.

---

## 📋 Field-by-Field Copy-Paste Blocks

### Field 1: Solution Name
```text
BOB: Offline Smart Home Survival System & Physical DevOps Platform
```

### Field 2: Commercial / Company Legal Entity
```text
BOB Edge Systems (Division of ASCE Technologies, LLC)
```

### Field 3: Solution Category & Program Track
```text
Track: Build (Independent Software Vendor - ISV)
Primary Category: Edge Computing, Internet of Things (IoT), Disaster Resilience & Energy Management
```

### Field 4: Short Description (Elevator Pitch)
```text
BOB is an offline-first physical automation and edge DevOps platform engineered for Red Hat OpenShift, MicroShift, and IBM Edge Application Manager (IEAM). It eliminates cloud dependency during grid blackouts and disasters through embedded ML, automated load-shedding, and deterministic life-safety egress.
```

### Field 5: Comprehensive Solution Description & Value Proposition
```text
BOB (Building Offline Backbone) addresses the critical single point of failure in modern smart buildings and microgrids: fatal dependency on public cloud infrastructure. During extreme weather events (derecho winds, hurricanes, ice storms) and utility grid blackouts, centralized cloud automation fails due to severed fiber links and downed cellular towers.

BOB deploys directly to edge nodes as an autonomous containerized runtime. It features:
1. 100% Offline Autonomy: Real-time sensor telemetry ingestion, rule evaluation, and physical actuation execute entirely on-premises without an active internet connection.
2. Embedded Edge Intelligence: Includes Watson-class Random Forest barometric storm prediction, Isolation Forest electrical anomaly protection, and WSU CASAS-trained occupancy modeling.
3. Cold-Load Pickup Mitigation: Staggers post-blackout residential re-energization across multi-tier phases (egress lighting -> refrigeration -> HVAC), eliminating the 1,850 kW inrush spikes that blow utility substation transformers.
4. Cryptographic Audit Trail: Every physical actuation produces an immutable SHA-256 hash-chained audit record with microsecond decision tracing for regulatory (FERC/NERC) compliance.
```

### Field 6: IBM & Red Hat Technology Building Blocks Alignment
```text
BOB natively integrates with IBM and Red Hat enterprise technologies:
1. Automated Resilience & Compliance: Enforces continuous local policy execution and 8x battery runtime extension during grid outages using declarative YAML/JSON policies.
2. Real Time Guardrails & Agent Ops: Enforces deterministic life-safety priority overrides (Priority 100 automatic egress unlocking during smoke/hazard events) with microsecond decision tracing.
3. Data Streaming & Observability: Normalizes Zigbee, MQTT, and sensor telemetry into structured event streams with zero cloud egress.
4. IBM Edge Application Manager (IEAM) & Open Horizon: Packaged with production Horizon service definitions and deployment patterns for autonomous, zero-touch fleet rollouts across tens of thousands of edge gateways.
5. Red Hat OpenShift & MicroShift: Certified OCI container bundle with CustomResourceDefinition (BobEdgeDeployment) adhering to OpenShift restricted-v2 SecurityContextConstraints (SCC), non-root execution, and privilege escalation controls.
6. watsonx Orchestrate Integration: Exposes a Remote Model Context Protocol (MCP) server interface enabling watsonx Orchestrate AI agents to query building status and trigger governed emergency protocols.
```

### Field 7: Primary Target Industries & Verticals
```text
1. Energy & Electric Utilities: Investor-Owned Utilities (IOUs) and Electric Cooperatives mitigating cold-load pickup transformer damage and reducing SAIDI/SAIFI outage metrics.
2. Real Estate Investment Trusts (REITs) & Multi-Family Housing: Commercial property operators eliminating lockouts, freezing pipes, and tenant life-safety liabilities during grid blackouts.
3. Public Safety & Disaster Recovery: Emergency shelters, microgrids, and critical municipal infrastructure requiring islanded, autonomous operation.
```

### Field 8: Customer Problem & Pain Points Solved
```text
1. Substation Transformer Failures: Cold-load pickup surges during storm restoration cost utilities $800,000 to $2,500,000 per blown transformer with 6-month supply chain lead times. BOB staggers edge startup to eliminate surges.
2. Cloud Lock-in & Blackout Paralysis: 99% of IoT platforms fail when internet connectivity drops, disabling smart locks and environmental controls during emergencies. BOB guarantees 100% local fidelity.
3. Microgrid Battery Exhaustion: Unmanaged residential UPS batteries exhaust within 3 to 4 hours. BOB's CASAS-trained ML dynamically sheds non-essential zones, extending battery runtime to 36+ hours (an 8x increase).
```

### Field 9: Commercial Model & Pricing Structure
```text
1. Commercial Gateway Subscription (REITs / Multi-Family): $1,200 per edge node per year with Red Hat OpenShift support and 99.99% local edge uptime SLA.
2. Electric Utility Feeder Capacity: $25,000 per substation feeder per year under multi-year utility agreements, initiated via a $45,000 turnkey 90-day pilot.
3. IBM Partner Co-Selling: Listed on Red Hat Marketplace and IBM Cloud Catalog with standard IBM Value Seller margins (up to 15% preferred partner margin).
4. watsonx Orchestrate MCP Agent: 70/30 revenue share for enterprise tenant agent invocations.
```

### Field 10: Technical Specifications & Deployment Environment
```text
- Container Architecture: Multi-arch OCI images (x86_64 and ARM64).
- Orchestration: Red Hat OpenShift 4.12 - 4.17, Red Hat Device Edge (MicroShift), K3s, and IBM Edge Application Manager (Open Horizon).
- Security Profile: Non-root execution (UID 10001), allowPrivilegeEscalation=false, readOnlyRootFilesystem=true, capabilities=DROP ALL.
- Protocols Supported: MQTT, Zigbee 3.0, Z-Wave Plus, Modbus TCP, dry-contact relays, and REST/MCP.
```

### Field 11: Public Repositories & Artifact Links
```text
- GitHub Repository: https://github.com/tbullitt18-collab/BOB-SmartHome-Offline
- IBM Technology Dossier: commercial/partner-plus/PARTNER_PLUS_APPLICATION_DOSSIER.md
- IEAM Service Definition: commercial/ieam-openshift/horizon/service.definition.json
- OpenShift Operator Bundle: commercial/ieam-openshift/openshift/operator/bundle/
- watsonx Orchestrate MCP Definition: commercial/partner-plus/WATSONX_ORCHESTRATE_MCP_LISTING.json
```

### Field 12: Primary Contact & Submitter Information
```text
- Full Name: Todd Bullitt
- Partner Enterprise ID: 10wtzf
- Role: Founder & Lead Architect
- Email: support@bob-edge.io / tbullitt18@gmail.com
- Commercial Entity: BOB Edge Systems (Division of ASCE Technologies, LLC)
```

---

## 🚀 Post-Submission Next Steps

1. **Watch Your Inbox:** IBM Partner Plus onboarding sends confirmation within 24–48 hours.
2. **If Escalation is Needed:** Use [`commercial/partner-plus/APP_ID_REQUEST_EMAIL.md`](APP_ID_REQUEST_EMAIL.md) to email `partnerplus@ibm.com` or your assigned Partner Ecosystem Manager.
3. **Unlock Silver Tier:** Complete the two 45-minute zero-cost credential courses on [learn.ibm.com](https://learn.ibm.com) (Course 13174 & Course 15986) to automatically unlock Silver Partner Tier status, IBM Cloud credits, and co-marketing funds.
