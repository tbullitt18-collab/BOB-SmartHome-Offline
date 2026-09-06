# COMMERCIAL PILOT SERVICES AGREEMENT
## DISTRIBUTED EDGE LOAD-SHEDDING & COLD-LOAD PICKUP MITIGATION

**EFFECTIVE DATE:** [INSERT DATE], 2026  
**PILOT REFERENCE ID:** `BOB-PILOT-UTIL-2026-01`  

---

### PARTIES

This Commercial Pilot Services Agreement (the **"Agreement"**) is entered into by and between:

1. **BOB Edge Systems** (a division of ASCE Technologies, LLC), an enterprise edge automation and grid resilience company having its principal place of business at [INSERT VENDOR ADDRESS] (**"Vendor"** or **"BOB"**), and
2. **[INSERT UTILITY COMPANY NAME]**, an electric utility corporation organized and operating under the laws of [INSERT STATE/PROVINCE], having its principal place of business at [INSERT UTILITY ADDRESS] (**"Utility"**).

Vendor and Utility are each referred to individually as a **"Party"** and collectively as the **"Parties."**

---

### RECITALS

**WHEREAS**, Utility operates electrical distribution infrastructure, including high-voltage distribution substations and radial distribution feeders serving residential and commercial customers;

**WHEREAS**, Utility experiences cold-load pickup challenges, excessive transformer inrush current, and severe risk of protective relay tripping or substation transformer thermal flashover following storm-related feeder blackouts;

**WHEREAS**, Vendor has developed proprietary, offline-first edge computing technology (**"BOB Platform"**) that provides autonomous, deterministic staggered re-energization and embedded machine learning load-shedding directly on customer premises without cloud dependency; and

**WHEREAS**, Utility desires to conduct a turnkey ninety (90) day proof-of-concept pilot on a designated distribution feeder to validate Vendor’s cold-load pickup mitigation, asset protection, and outage restoration capabilities.

**NOW, THEREFORE**, in consideration of the mutual covenants contained herein and other good and valuable consideration, the Parties agree as follows:

---

### 1. SCOPE OF WORK & PILOT DELIVERABLES

1.1 **Pilot Cohort:** Vendor shall configure, deploy, and monitor fifty (50) BOB Edge Gateway nodes on a single designated 13.8 kV or 12.47 kV distribution feeder identified by Utility (the **"Target Feeder"**).

1.2 **Hardware & Installation:** 
   * Vendor shall provide fifty (50) industrial-grade BOB Edge Gateway appliances with DIN-rail mountings, local Zigbee/Relay interfaces, and integrated battery-backed real-time clocks.
   * Installation may occur either in utility-owned meter bases, secondary distribution panelboards, or participating customer smart subpanels.

1.3 **Pilot Deliverables:** Vendor shall provide Utility with the following:
   * **D-1: Deployment & Commissioning Report:** Verification of 50 operating edge nodes communicating locally on the Target Feeder.
   * **D-2: Autonomous Cold-Load Pickup Test:** Measured telemetry data verifying deterministic four-tier staggered startup during controlled feeder switching or storm simulation.
   * **D-3: Inrush Reduction Analysis:** Comparative analysis of peak inrush demand (kW), power factor stabilization, and transformer thermal loading.
   * **D-4: Final Engineering Evaluation & ROI Report:** Comprehensive executive report detailing avoided transformer wear, outage duration reduction (SAIDI/SAIFI), and financial business case for system-wide expansion.

---

### 2. PILOT TERM & IMPLEMENTATION SCHEDULE

2.1 **Term:** The duration of this pilot shall be ninety (90) calendar days commencing on the Effective Date (the **"Pilot Term"**), structured across three phases:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            90-DAY PILOT TIMELINE                            │
├──────────────────────┬──────────────────────┬───────────────────────────────┤
│ PHASE 1: DAYS 1–30   │ PHASE 2: DAYS 31–60  │ PHASE 3: DAYS 61–90           │
│ Hardware Provisioning│ Active Telemetry &   │ Data Harmonization,           │
│ & Feeder Deployment  │ Storm Simulation     │ Engineering Report & Board ROI│
└──────────────────────┴──────────────────────┴───────────────────────────────┘
```

2.2 **Milestones:**
* **Phase 1 (Days 1–30):** Feeder selection, appliance provisioning, gateway commissioning, baseline load profile logging.
* **Phase 2 (Days 31–60):** Controlled re-energization testing, offline storm mode validation, and localized load-shedding verification.
* **Phase 3 (Days 61–90):** Telemetry aggregation, IEEE C57.91 transformer thermal evaluation, and delivery of final engineering report.

---

### 3. PRICING, FEES & PAYMENT TERMS

3.1 **Fixed Pilot Fee:** Utility agrees to pay Vendor a flat, all-inclusive fee of **Forty-Five Thousand U.S. Dollars ($45,000.00 USD)** for the complete 90-day pilot program.

3.2 **Milestone Invoicing Schedule:**
* **Milestone 1 ($15,000 USD):** Due within fifteen (15) days of the Effective Date (Hardware provisioning and kickoff).
* **Milestone 2 ($15,000 USD):** Due upon completion of Phase 1 and delivery of Deliverable D-1 (Commissioning Report).
* **Milestone 3 ($15,000 USD):** Due upon completion of Phase 3 and delivery of Deliverable D-4 (Final Engineering Report).

3.3 **Payment Terms:** All invoices shall be payable Net 30 days from date of receipt.

---

### 4. INTELLECTUAL PROPERTY & DATA RIGHTS

4.1 **Vendor Intellectual Property:** Vendor retains all right, title, and interest in and to the BOB Platform, software binaries, edge orchestration algorithms, Scikit-Learn machine learning weights, firmware, and associated documentation. No title to or ownership of Vendor IP is transferred to Utility.

4.2 **Utility Data Ownership:** Utility retains sole ownership of all raw electrical grid telemetry, substation SCADA metrics, and customer meter data collected during the Pilot.

4.3 **Evaluation License:** Vendor grants Utility a temporary, non-exclusive, non-transferable, royalty-free license to access and evaluate the BOB Platform during the Pilot Term solely for testing on the Target Feeder.

---

### 5. CYBERSECURITY, NERC CIP & AIR-GAP COMPLIANCE

5.1 **100% Offline Edge Autonomy:** Vendor warrants that the BOB Platform requires zero active internet or cloud connection to perform its core governor functions. All load-shedding and staggered re-energization algorithms execute locally on-premises.

5.2 **Zero Cloud Egress:** No customer data, building telemetry, or grid operational parameters shall be transmitted to third-party public cloud providers without express prior written approval from Utility.

5.3 **NERC CIP Alignment:**
* Gateways operate with closed inbound network ports.
* Local inter-node communication utilizes authenticated, encrypted local protocols (AES-128 / TLS 1.3).
* All load-shed actions are logged with immutable, SHA-256 cryptographic audit hashes compliant with NERC CIP-005 and CIP-007 event logging guidelines.

---

### 6. SAFETY, WARRANTIES & LIMITATION OF LIABILITY

6.1 **Fail-Safe Operation:** Vendor warrants that in the event of gateway controller hardware failure or logic freeze, all electrical circuits managed by BOB shall default to a **"Fail-Closed" (Grid Pass-Through)** state, ensuring that customer electrical service is never arbitrarily interrupted due to software anomaly.

6.2 **Warranty Disclaimer:** EXCEPT AS EXPRESSLY SET FORTH HEREIN, VENDOR PROVIDES THE PILOT HARDWARE AND SOFTWARE ON AN "AS-IS, AS-TESTED" BASIS FOR EXPERIMENTAL AND EVALUATION PURPOSES.

6.3 **Limitation of Liability:** To the maximum extent permitted by applicable law, neither Party shall be liable for consequential, indirect, punitive, or special damages. Each Party's total aggregate liability arising out of or related to this Agreement shall be limited to the total fees paid or payable by Utility under this Agreement ($45,000 USD).

---

### 7. POST-PILOT PRODUCTION EXPANSION OPTION

7.1 **Enterprise Rollout Rights:** Upon successful completion of the Pilot Term, Utility shall have the exclusive option for a period of ninety (90) days to enter into an Enterprise Master Services Agreement (MSA) with Vendor to deploy the BOB Platform across additional distribution feeders.

7.2 **Guaranteed Commercial Pricing:** Under the MSA, Utility shall be entitled to preferred enterprise pricing of **Twenty-Five Thousand U.S. Dollars ($25,000.00 USD) per substation feeder per year**, including enterprise OpenShift / IBM Edge Application Manager fleet management and 24/7/365 Tier 1 emergency support.

---

### 8. GENERAL PROVISIONS

8.1 **Governing Law:** This Agreement shall be governed by and construed in accordance with the laws of [INSERT GOVERNING STATE/JURISDICTION], without regard to its conflict of laws principles.

8.2 **Entire Agreement:** This Agreement, including its Exhibits, constitutes the entire agreement between the Parties and supersedes all prior oral or written discussions, agreements, or proposals.

---

### IN WITNESS WHEREOF, the Parties have executed this Commercial Pilot Services Agreement as of the Effective Date.

```text
FOR: [INSERT UTILITY COMPANY NAME]             FOR: BOB EDGE SYSTEMS
                                                    (ASCE Technologies, LLC)

Signature: ______________________________      Signature: ______________________________
Printed:   ______________________________      Printed:   Todd Bullitt
Title:     ______________________________      Title:     Founder & Chief Architect
Date:      ______________________________      Date:      ______________________________
```

---

### EXHIBIT A: TECHNICAL SPECIFICATIONS & FEEDER SCOPE

* **Target Feeder Voltage:** 12.47 kV / 13.8 kV distribution circuit
* **Substation Transformer Capacity:** 1,000 kVA to 5,000 kVA
* **Edge Node Population:** 50 residential premises
* **Governor Tiers:**
  * Tier 1: Life-Safety & Gateway (T+0s)
  * Tier 2: Refrigeration with jitter (T+60s)
  * Tier 3: Water Heating banks (T+180s)
  * Tier 4: HVAC Compressors with CASAS shedding (T+420s)
* **Maximum Feeder Demand Cap:** ≤ 410 kW during re-energization phase

---

### EXHIBIT B: SUPPORT & SERVICE LEVEL TERMS

* **Phase 1 Commissioning Support:** Dedicated on-site or remote engineering support 8:00 AM – 5:00 PM local time.
* **Phase 2 & 3 Operational Support:** 24/7 on-call engineering response for controlled feeder switching tests and active storm response.
* **Severity 1 Emergency Response:** Within 15 minutes for any condition affecting grid safety.
