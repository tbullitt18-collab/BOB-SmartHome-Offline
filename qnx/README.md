# ASCE Deterministic Safety Core — QNX OS 8.0

Native C99 cyber-physical safety arbiter, **QNX Resource Manager daemon (`/dev/asce_arbiter`)**, and multi-process IPC pipeline ported from **BOB Offline** and **AquaPulse OS** for **QNX OS 8.0** (QNX Everywhere / QNX SDP 8.0).

## Architecture (Microkernel + Resource Manager + Native IPC)

1. **QNX Resource Manager Service (`src/resmgr.c` -> `asce_arbiterd`)**
   - Publishes **`/dev/asce_arbiter`** via `dispatch_create()`, `iofunc_func_init()`, `iofunc_attr_init()`, and `resmgr_attach()` (`_FTYPE_ANY`).
   - **Real-Time & Pulse Watchdog:** Elevates to **`SCHED_FIFO` priority 20** and attaches a `500 ms` `CLOCK_MONOTONIC` kernel timer (`SIGEV_PULSE_INIT` + `pulse_attach()` + `message_connect()`).
   - **Least-Privilege Microkernel Hardening:** Before servicing untrusted clients, locks down capabilities via `procmgr_ability()` (`PROCMGR_AOP_DENY | PROCMGR_AOP_LOCK` on `PROCMGR_AID_SPAWN`, `PROCMGR_AID_FORK`, `PROCMGR_AID_REBOOT`, `PROCMGR_AID_PATHSPACE`, `PROCMGR_AID_MEM_SPECIAL`) and drops root privileges to unprivileged **`uid=1001 gid=1001`**.
   - **Kernel-Authenticated Caller Auditing:** Inspects caller `(pid, euid)` using `iofunc_client_info_ext()` on every write and `devctl()`.
   - **Dual Interface:**
     - **POSIX VFS (`read` / `write`):** Supports `echo "bypass=0" > /dev/asce_arbiter`, `echo "start=all" > /dev/asce_arbiter`, `echo "shed=medical_oxygen_conc" > /dev/asce_arbiter` (returns `EACCES`), and `cat /dev/asce_arbiter`.
     - **Binary `devctl()` (`src/asce_devctl.h`):** `DCMD_ASCE_EVAL` (`__DIOTF`) and `DCMD_ASCE_STATS` (`__DIOF`) evaluated by decoupled external clients (`src/client.c` -> `asce_ctl`).

2. **Decoupled 3-Process Synchronous IPC Core (`src/main.c` + `src/ipc.c` -> `asce_safety_core`)**
   ```text
     [Sensor Process] ──(MsgSend safety_req_t)──▶ [Arbiter Process (SCHED_FIFO prio=20)]
            │                                                   │
            │ ◀────────────(MsgReply safety_rep_t + SHA-256)────┘
            │
            └──(MsgSend actuator_cmd_t)────────▶ [Actuator Process]
                                                   └─ verifies SHA-256 receipt & verdict before actuation
   ```
   - Uses `<sys/neutrino.h>` (`ChannelCreate`, `ConnectAttach`, `MsgSend`, `MsgReceive`, `MsgReply`) when compiled with `qcc` (`__QNX__`).
   - Enforces three deterministic invariants (`src/safety.c`, `src/sha256.c`):
     1. **EPA 20 PSI Hydraulic Interlock (`MSG_HYDRAULIC`):** Intercepts `0.0%` bypass at `16.20 PSI` (`< 20.0 PSI`) and enforces `APPROVED_MODIFIED` (`25.0%` PRV-3 bypass → `98.62 PSI` at `St. Jude J-42`).
     2. **NEC Cold-Load Inrush Governor (`MSG_START_LOADS`):** Orders motors by descending excess inrush (`inrush - run`) and staggers across `4` steps (`1500 ms`), bounding `89.0 A` simultaneous inrush to `50.0 A`.
     3. **Life-Safety Firewall (`MSG_SHED_LOAD`):** Deterministically rejects (`DEC_REJECTED` / `EACCES`) load shedding targeting `medical_oxygen_conc`.

## Pre-Existing vs. Built During Hackathon

- **Pre-existing before Nov 2, 2026:** Python prototypes for BOB Offline and AquaPulse OS in the rest of this repository (`engine/`, `scripts/`, `policies/`, web UIs).
- **Built during the hackathon (Nov 2 – Dec 15, 2026):** Root open-source `LICENSE` (MIT) and the entire `qnx/` directory — native C99 safety arbiter, QNX Resource Manager (`/dev/asce_arbiter`), `procmgr_ability` least-privilege locking, `CLOCK_MONOTONIC` pulse watchdog, `devctl()` client, `mkqnximage` boot-startup snippets (`qemu/snippets/`), cross-process Neutrino 8.0 IPC layer, multi-architecture `Makefile` (`x86_64` and `aarch64le`), and QEMU OS 8.0 benchmarks.

## Build & Run on QNX SDP 8.0 (QEMU x86_64)

### 1. Cross-compile with `qcc`

From an SDP 8.0 environment (`qnxsdp-env.sh` on Linux or `qnxsdp-env.bat` on Windows):

```sh
cd qnx
make                 # outputs build/x86_64/{asce_safety_core,asce_arbiterd,asce_ctl}
# Optional for ARM64 targets:
make ARCH=aarch64le  # outputs build/aarch64le/{asce_safety_core,asce_arbiterd,asce_ctl}
```

### 2. Boot Customization (`mkqnximage`)

Copy the compiled binaries and repo startup snippets into an empty `mkqnximage` VM workspace so QNX OS 8.0 automatically starts `asce_arbiterd -U 1001:1001 -d` and registers `/dev/asce_arbiter` at boot:

```sh
mkdir -p local/snippets
cp /path/to/qnx/build/x86_64/{asce_safety_core,asce_arbiterd,asce_ctl} ./
cp /path/to/qnx/qemu/snippets/{data_files.custom,post_start.custom} local/snippets/
mkqnximage --type=qemu --arch=x86_64 --tcg=yes --noprompt --ssh-ident=none --build --force
```

## Measured QNX OS 8.0 Execution & Benchmark Output (QEMU x86_64 TCG)

Measured live inside QEMU 9.0.2 (`qemu-system-x86_64`, TCG software emulation) running QNX SDP 8.0.0 (`2026/10/30-09:10:05EDT x86pc x86_64`):

```text
---> Starting ASCE QNX Resource Manager (/dev/asce_arbiter)
Process count:22
Startup complete
QNX noname 8.0.0 2026/10/30-09:10:05EDT x86pc x86_64
# ls -l /dev/asce_arbiter
crw-rw-rw-  1 root root 0,   1 2026-11-19 00:11 /dev/asce_arbiter
# echo "bypass=0" > /dev/asce_arbiter
# echo "shed=medical_oxygen_conc" > /dev/asce_arbiter || echo "FIREWALL_BLOCKED_EACCES (exit=$?)"
FIREWALL_BLOCKED_EACCES (exit=1)
# cat /dev/asce_arbiter
ASCE QNX OS 8.0 Safety Arbiter (/dev/asce_arbiter)
daemon_pid=290834 uid=1001 gid=1001 sched=SCHED_FIFO(20) abilities_locked=1 watchdog_pulses=5
evals=2 approved=0 modified=1 rejected=1
last_caller_pid=57351 last_caller_uid=0
last_verdict=REJECTED reason=LIFE_SAFETY_LOAD_PROTECTED
last_hydraulic_psi=98.62 applied_bypass_pct=25.0 last_peak_amps=0.0
last_sha256=7aee4a48e2c70bd3a414a7f0130bd06d61ca48b8b7d6e196ae095f33d74370b9

# /data/home/root/asce_ctl
[ResMgr Scenario 1: P-4 Isolation (0% Bypass -> Overridden)]
  ResMgr(/dev/asce_arbiter) -> APPROVED_MODIFIED (EPA_20_PSI_INTERLOCK_PRV3_BYPASS) | devctl IPC: 1044.99 us | seq=3
  Hydraulic -> Req Bypass: 0.0% | Applied Bypass: 25.0% | St. Jude (J-42): 98.62 PSI
  Kernel Creds -> Caller PID=425986 UID=0 | SHA-256 Verified=OK (ea32b273c4f69669...)
[ResMgr Scenario 2: Cold-Load Pickup (89A -> 50A Stagger)]
  ResMgr(/dev/asce_arbiter) -> APPROVED_MODIFIED (NEC_INRUSH_STAGGER_ENFORCED) | devctl IPC: 2376.80 us | seq=4
  Electrical-> Peak Current Bounded: 50.0 A | Stagger Steps: 4 | Planned Delay: 1500 ms
  Kernel Creds -> Caller PID=425986 UID=0 | SHA-256 Verified=OK (85329c28ea58d310...)
[ResMgr Scenario 3: Unauthorized Medical O2 Shed]
  ResMgr(/dev/asce_arbiter) -> REJECTED (LIFE_SAFETY_LOAD_PROTECTED) | devctl IPC: 483.48 us | seq=5
  Firewall  -> Target Load: medical_oxygen_conc | Actuation Allowed: 0
  Kernel Creds -> Caller PID=425986 UID=0 | SHA-256 Verified=OK (08d630610380f8e3...)

[ResMgr devctl Benchmark: 1,000 Cycles (Baseline)] 1000 cycles in 306.97 ms (3258 Hz)
  /dev/asce_arbiter devctl() Latency: mean=303.82 us | p95=510.52 us | p99=847.93 us | max=2177.74 us
[ResMgr devctl Benchmark: 1,000 Cycles (Under CPU Load Contention)] 1000 cycles in 265.40 ms (3768 Hz)
  /dev/asce_arbiter devctl() Latency: mean=262.67 us | p95=499.90 us | p99=1020.25 us | max=3978.70 us

# /data/home/root/asce_safety_core
[Benchmark: 1,000 Cycles (Baseline)] 1000 cycles in 275.70 ms (3627 Hz)
  Round-Trip Arbiter IPC Latency: mean=273.06 us | p95=575.24 us | p99=1094.48 us | max=2855.67 us
[Benchmark: 1,000 Cycles (Under CPU Load Contention)] 1000 cycles in 530.76 ms (1884 Hz)
  Round-Trip Arbiter IPC Latency: mean=528.27 us | p95=1382.50 us | p99=3181.46 us | max=6464.50 us
[DONE] Clean shutdown of 3-process safety loop.
```
