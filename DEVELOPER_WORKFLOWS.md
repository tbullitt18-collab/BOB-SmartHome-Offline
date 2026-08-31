# BOB: Physical Automation DevOps Platform

> **Bridging the gap between developer workflow pains and physical smart home hardware by treating the home as an observable, testable, local edge runtime.**

---

## 1. The Core Product Shift
Most consumer smart home products are closed, fragile, and command-centric ("turn on light", "view camera"). When systems fail, developers face distributed systems pains with zero operational tooling:
- **No Test Environment:** You cannot simulate a storm, power spike, or sensor fault without risking physical hardware.
- **Invisible Decisions:** Zero audit trail or decision traces explaining *why* an automation locked a door or cut power.
- **Untestable Automations:** Rules scattered across proprietary vendor apps without Git version control or PR reviews.
- **Cloud Outage Brittleness:** Cloud APIs go down precisely when physical emergency automation is needed most.

**BOB transforms smart homes into an Edge Automation Platform for physical workflows.**

---

## 2. Developer Workflow Matrix

| Developer Workflow Pain | Smart Home Manifestation | BOB Capability |
|---|---|---|
| **Debugging Distributed Systems** | Sensor triggers inconsistently or device drops silently | Structured Decision Traces with event ID, policy version, AI confidence, and sub-millisecond execution latency |
| **No Test Environment** | Cannot test outage/storm behavior without breaking live home | Deterministic `simulator/event_replay.py` and `simulator/device_emulator.py` for CI/CD regression testing |
| **Hard-to-Review Logic** | Unsafe, untracked automation rules | Automation-as-Code: Versioned YAML policies (`policies/`) governed by JSON Schema contracts (`contracts/`) |
| **No Audit Trail** | Unexplainable HVAC or lock state changes | Append-only, SHA-256 hash-chained `observability/audit_trail.jsonl` |
| **Vendor Lock-in** | Incompatible protocols (Zigbee, Z-Wave, REST) | Canonical normalized event bus (`engine/event_bus.py`) |
| **Deployment Drift** | Automations work in one house but fail in another | Environment profiles for `deploy/dev`, `deploy/staging`, and `deploy/production` |
| **Alert Fatigue** | Low-value notification spam | Multi-tier priority: Informational (50), Hardware Anomaly (70), Storm Resilience (90), Safety Hazard (100) |

---

## 3. BOB Pipeline Architecture

```text
Device / Sensor Event
        ↓
    Event Bus (Normalized Contract)
        ↓
  Policy Engine (Deterministic Safety Rules First)
        ↓
   AI Decision (Optimization, Storm Risk & Anomaly Scoring)
        ↓
Consequential Action Approval Gate (PIN / Local Policy)
        ↓
Hardware Execution (Zigbee / Z-Wave / Relay Actuation)
        ↓
Observable Decision Trace + Cryptographic Audit Log + Graphite Metrics
```

---

## 4. Key Workflows

### 🌩️ Offline Storm Mode (Operational Runbook)
- **Trigger:** Local barometric pressure drop (< 990 hPa) detected by offline `StormPredictor`.
- **Action:** Enters Storm Mode, sheds non-essential lighting and HVAC in vacant zones based on CASAS occupancy routines, pre-charges battery backups, and surfaces local LAN dashboard status.

### 💻 Developer Ambient Focus Mode (CI/CD Signaling)
- **Trigger:** Git branch switch (`feature/*`) or GitHub Actions CI webhook (`passed` / `failed`).
- **Action:** Adjusts office lighting to deep focus scene, mutes non-critical notifications for 90 minutes, and pulses ambient LED strips in real-time response to CI build passes (green) or failures (red).

### ⚡ Electrical Anomaly Protection
- **Trigger:** `power.draw.changed` exceeding safety baseline.
- **Action:** Evaluated by `IsolationForest` anomaly detector. Isolates faulty smart plug or circuit before thermal runaway or electrical fire occurs.

### 🔁 Automation DevOps Loop (CI/CD Replay)
- **Trigger:** Git commit modifying a policy file in `policies/`.
- **Action:** Replays historic event streams through `simulator/event_replay.py` to verify 100% decision determinism before promoting policy from `staging/` to `production/`.

---

## 5. Verification & Testing

Run the full end-to-end Automation DevOps Loop verification script:

```bash
python scripts/demo_devops_loop.py
```
