# Enterprise Pricing, Licensing & Service Level Agreement (SLA)

**Platform:** BOB Edge Automation & Disaster Resiliency Engine  
**Vendor:** BOB Edge Systems  
**Effective Date:** 2026-09-01  

---

## 1. Commercial Pricing Matrix

```text
┌───────────────────────────┬───────────────────────────┬───────────────────────────┐
│     TIER 1: COMMUNITY     │    TIER 2: COMMERCIAL     │     TIER 3: UTILITY       │
│        (Open Source)      │       (Multi-Family)      │       (Grid Enterprise)   │
├───────────────────────────┼───────────────────────────┼───────────────────────────┤
│ • $0 Free License         │ • $1,200 / node / year    │ • $25,000 / sub / year    │
│ • Single edge node        │ • Up to 250 endpoints     │ • Unlimited cluster nodes │
│ • Local YAML policies     │ • Red Hat OpenShift Cert  │ • IEAM Automated Rollout  │
│ • Community forum support │ • Priority 8x5 support    │ • 24/7/365 Emergency SLA  │
│ • Standard event replay   │ • Immutable Audit Logs    │ • Feeder Inrush Governor  │
└───────────────────────────┴───────────────────────────┴───────────────────────────┘
```

---

## 2. Hardware Appliance Bundles (Optional Turnkey Edge)

For enterprise clients requiring pre-certified hardware appliances:
- **BOB Edge Gateway 100 (ARM64):** $499 per unit (Industrial DIN-rail mounted gateway with Zigbee 3.0 / Z-Wave Plus transceivers, 8GB RAM, 64GB NVMe storage, dual Gigabit LAN, and battery-backed RTC).
- **BOB Substation Rackmount 2000 (x86_64):** $2,499 per unit (1U rackmount industrial server with redundant power supplies, hardware watchdog timer, and isolated dual Ethernet).

---

## 3. Enterprise Service Level Agreement (SLA)

### A. Local Edge High Availability (Uptime: 99.99%)
- Because BOB operates 100% locally with zero cloud dependencies, local physical automation, sensor telemetry ingestion, and safety overrides maintain a **99.99% local edge uptime guarantee**.

### B. Incident Support Response Tiers
| Severity Level | Definition | Response Time | Target Resolution |
|---|---|---|---|
| **Severity 1 (Critical)** | Complete building blackout failure, life-safety egress lock failure | **< 15 minutes** (24/7/365) | Immediate emergency hotfix |
| **Severity 2 (High)** | Sensor mesh degraded, AI inference offline, single cluster replica down | **< 2 hours** (Business hours) | Workaround in < 8 hours |
| **Severity 3 (Normal)** | Configuration drift, non-critical telemetry reporting issue | **< 1 business day** | Next regular patch release |

### C. Data Privacy & Zero Cloud Egress Guarantee
- All telemetry, sensor logs, occupancy heatmaps, and cryptographic audit records remain strictly on-premises.
- Zero customer data is transmitted to public cloud providers or third parties unless explicitly configured by the customer.
