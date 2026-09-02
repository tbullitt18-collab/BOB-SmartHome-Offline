# Commercial Pilot Proposal: Electric Utilities & Microgrid Resiliency

**Proposal Title:** Distributed Edge Load-Shedding & Cold-Load Pickup Mitigation Pilot  
**Target Clients:** Investor-Owned Utilities (IOUs), Electric Cooperatives, Municipal Utilities, Virtual Power Plant (VPP) Aggregators  
**Vendor:** BOB Edge Systems  
**Primary Contact:** Todd Bullitt  

---

## 1. The Utility Challenge: The Cold-Load Pickup Catastrophe

When high-impact weather events (hurricanes, ice storms, derecho windstorms) cause widespread feeder blackouts, re-energization represents one of the most hazardous phases for utility distribution operations:
1. **Cold-Load Pickup Surges:** When a feeder is re-energized, every residential compressor, heat pump, water heater, and refrigerator draws startup locked-rotor amperage simultaneously.
2. **Substation Damage:** This surge routinely exceeds feeder protective relay limits, blowing substation transformers and causing secondary cascading outages.
3. **Black-Start Communication Latency:** Centralized cloud-based Demand Response (DR) platforms fail during severe events due to cellular tower outages and severed fiber links.

---

## 2. The BOB Utility Solution

BOB operates as an **Autonomous Edge Grid Governor** that requires **zero cloud communication** during disaster recovery:

```text
[ Grid Utility Distribution Feeder ]
                 │ (Power Restored)
                 ▼
 ┌────────────────────────────────────────────────────────┐
 │ BOB Edge Governor on Premises / Building Main Panel    │
 ├────────────────────────────────────────────────────────┤
 │ 1. Senses frequency & voltage stabilization            │
 │ 2. Enforces deterministic STAGGERED RE-ENERGIZATION   │
 │    - Life-safety lighting & egress: T+0 seconds        │
 │    - Communications & low-draw loads: T+120 seconds    │
 │    - Heavy inductive HVAC / Motors: T+300-600 seconds  │
 │ 3. Dynamically sheds non-essential zones (CASAS ML)    │
 └────────────────────────────────────────────────────────┘
                 │
                 ▼
  Protects Substation Transformer & Stabilizes Local Grid
```

---

## 3. Pilot Program Scope & Deliverables

### Phase 1: Substation Feeder Proof of Concept (60 Days)
- **Deployment:** 50 residential edge gateways across a single high-risk feeder zone.
- **Hardware Integration:** Compatible with standard smart electrical subpanels, Zigbee relays, and Home Assistant / K3s edge gateways.
- **Key Metric:** Real-world simulation and live tracking of peak inrush current reduction during feeder re-energization.

### Phase 2: Autonomous Islanding & Storm Mode Validation (90 Days)
- Validate autonomous transition to offline Storm Mode when feeder drops.
- Demonstrate UPS / battery runtime extension using CASAS occupancy learning.
- Verify tamper-evident cryptographic audit logs for regulatory compliance (FERC / NERC).

---

## 4. Projected Financial Return on Investment (ROI)

| Risk Category | Traditional Cost to Utility | Cost with BOB Deployment | Savings / ROI |
|---|---|---|---|
| **Blown Substation Transformer Replacement** | $800,000 – $2,500,000 + 6-month lead time | $0 (Prevented via staggered edge startup) | **$800k+ per incident** |
| **Truck Rolls for Manual Feeder Re-fusing** | $1,200 per truck roll | Automated edge self-healing | **75% reduction** |
| **Customer Outage Duration (SAIDI / SAIFI)** | High regulatory penalties | 40% faster feeder restoration | **Direct regulatory compliance** |

---

## 5. Pilot Pricing & Engagement Terms
- **Pilot Package Fee:** $45,000 flat (covers 50 edge gateway licenses, configuration, utility telemetry integration, and full engineering evaluation report).
- **Expansion Model:** $25,000 / substation feeder / year under enterprise master service agreement.
