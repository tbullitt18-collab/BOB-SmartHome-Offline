# IBM Partner Plus "Build" Track Application Dossier

Use this guide and pre-filled application responses to register BOB in the **IBM Partner Plus** portal at [ibm.com/partnerplus](https://www.ibm.com/partnerplus).

---

## 1. Company & Solution Profile

**Company / Project Name:** BOB Edge Systems  
**Primary Contact:** Todd Bullitt  
**Repository URL:** https://github.com/tbullitt18-collab/BOB-SmartHome-Offline  
**Program Track:** Build Track (Independent Software Vendor - ISV)  
**Primary Industry:** Energy & Utilities, Real Estate & Construction, Public Sector / Emergency Management  

---

## 2. Pre-Filled Application Form Fields

### Q1: Solution Description & Value Proposition
> **Answer:**  
> BOB (Building Offline Backbone) is an offline-first physical automation and edge DevOps platform. It eliminates the single point of failure inherent in cloud-dependent smart buildings and microgrids by running 100% locally on edge nodes. BOB embeds Watson-class machine learning models (Random Forest for barometric storm prediction, Isolation Forest for power anomaly detection, and CASAS-trained human occupancy models) directly on the edge hardware. It executes deterministic safety rules, dynamic load shedding during power outages (extending UPS battery life from 4 to 36+ hours), and emits immutable, SHA-256 hash-chained audit traces.

### Q2: How does your solution integrate with IBM and Red Hat technologies?
> **Answer:**  
> BOB is architected as an OCI-compliant containerized workload natively compatible with Red Hat OpenShift, Red Hat Device Edge (MicroShift), and K3s. It integrates directly with **IBM Edge Application Manager (IEAM)** via Open Horizon service definitions and patterns for autonomous edge lifecycle management across remote, offline facilities. Furthermore, BOB incorporates IBM Watson-class predictive patterns for local edge inference, and exports time-series metrics compatible with IBM Cloud and Graphite/Grafana monitoring stacks.

### Q3: What is the primary customer pain point and target market?
> **Answer:**  
> Our primary targets are:
> 1. **Electric Utilities & Cooperatives:** Suffer catastrophic transformer blowouts caused by cold-load pickup surges when re-energizing storm-damaged grids. BOB provides automated, staggered local load re-engagement.
> 2. **Multi-Family Housing Authorities & REITs:** Vulnerable to resident lockouts and life-safety failures when cloud systems disconnect during power outages.
> 3. **Industrial Edge Facilities:** Require observable, testable Automation-as-Code with verifiable decision traces and zero cloud dependency.

### Q4: What is your commercialization and revenue model?
> **Answer:**  
> BOB operates on a hybrid licensing model:
> - Annual per-gateway commercial subscription ($1,200/node/year) for multi-family property management.
> - Enterprise capacity tiers ($25,000/substation/year) for utilities managing smart microgrid territory.
> - Packaged for co-selling through the Red Hat Marketplace and IBM Cloud Catalog with full enterprise support SLAs.

---

## 3. Submission Checklist

- [x] Solution Brief created: `commercial/partner-plus/SOLUTION_BRIEF.md`
- [x] Red Hat Marketplace metadata configured: `commercial/partner-plus/marketplace-listing.json`
- [x] OCI Container and Kubernetes manifests verified
- [x] Open Horizon / IEAM deployment patterns ready: `commercial/ieam-openshift/horizon/`
- [x] Public GitHub repository accessible: https://github.com/tbullitt18-collab/BOB-SmartHome-Offline
- [ ] Submit application at [ibm.com/partnerplus](https://www.ibm.com/partnerplus)
