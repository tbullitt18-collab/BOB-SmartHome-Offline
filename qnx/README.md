# ASCE Deterministic Safety Core — QNX OS 8.0

Native C port of the deterministic cyber-physical safety arbiter from **BOB Offline** and **AquaPulse OS** targeting **QNX OS 8.0** (QNX Everywhere / QNX SDP 8.0).

## Architecture (3-Process QNX IPC Pipeline)

```
  [Sensor Process] ──(MsgSend safety_req_t)──▶ [Arbiter Process (SCHED_FIFO prio=20)]
         │                                                   │
         │ ◀────────────(MsgReply safety_rep_t + SHA-256)────┘
         │
         └──(MsgSend actuator_cmd_t)────────▶ [Actuator Process]
                                                └─ verifies SHA-256 receipt & verdict before actuation
```

- **Sensor process**: Emits hydraulic isolation requests, post-outage motor cold-load startup masks, and load-shed commands over QNX synchronous message passing.
- **Safety-arbiter process (`SCHED_FIFO`, priority `20`)**:
  1. **EPA 20 PSI Hydraulic Interlock (`MSG_HYDRAULIC`)**: Evaluates downstream hospital junction `J-42` pressure (`hydraulic_predict_psi`). Unmitigated direct isolation (`0%` bypass) predicts `16.20 PSI` (`< 20.0 PSI`), so the arbiter overrides with `APPROVED_MODIFIED` + `25.0%` `PRV-3` bypass (`98.62 PSI`).
  2. **NEC Cold-Load Inrush Governor (`MSG_START_LOADS`)**: Orders enabled inductive loads by descending excess inrush (`inrush - run`) and spaces starts by `500 ms` steps (`1500 ms` total for 4 loads), bounding peak startup current from `89.0 A` simultaneous down to `50.0 A` (`<= BREAKER_LIMIT_AMPS`).
  3. **Life-Safety Load-Shed Firewall (`MSG_SHED_LOAD`)**: Deterministically rejects (`DEC_REJECTED`) load-shedding targeting protected medical equipment (`medical_oxygen_conc`).
  4. **Cryptographic Audit Receipt**: Computes an in-process FIPS 180-4 SHA-256 digest (`sha256.c`) over every decision tuple.
- **Actuator process**: Independently recomputes and verifies the arbiter's SHA-256 receipt and verdict before executing physical stagger delays or reporting actuation.

When compiled with `qcc` (`__QNX__`), [`src/ipc.c`](src/ipc.c) binds directly to `<sys/neutrino.h>` (`ChannelCreate`, `ConnectAttach`, `MsgSend`, `MsgReceive`, `MsgReply`). On non-QNX POSIX hosts (`#ifndef __QNX__`), a `pthread`/shared-memory shim allows compiling and unit-testing the state machine on Linux (`make test-host`).

## Pre-Existing vs. Built During Hackathon

- **Pre-existing before Nov 2, 2026**: Python prototypes for BOB Offline and AquaPulse OS in the rest of this repository (`engine/`, `scripts/`, `policies/`, web UIs).
- **Built during the hackathon (Nov 2 – Dec 15, 2026)**: Root open-source `LICENSE` (MIT) and the entire `qnx/` directory — native C99 port of the safety arbiter, SHA-256 receipt verification, `SCHED_FIFO` priority scheduling, cross-process QNX Neutrino 8.0 IPC layer, multi-architecture `Makefile` (`x86_64` and `aarch64le`), and QEMU OS 8.0 benchmarks.

## Build & Run on QNX SDP 8.0 (QEMU x86_64)

### 1. Cross-compile with `qcc`

From an SDP 8.0 environment (`qnxsdp-env.sh` on Linux or `qnxsdp-env.bat` on Windows):

```sh
cd qnx
make                 # outputs build/x86_64/asce_safety_core
# Optional for ARM64 targets:
make ARCH=aarch64le  # outputs build/aarch64le/asce_safety_core
```

### 2. Build & boot QNX OS 8.0 QEMU image

In an empty VM workspace directory:

```sh
mkdir -p local/snippets
cp /path/to/qnx/build/x86_64/asce_safety_core ./asce_safety_core
echo '[uid=0 gid=0 perms=0755] home/root/asce_safety_core=asce_safety_core' > local/snippets/data_files.custom
mkqnximage --type=qemu --arch=x86_64 --tcg=yes --noprompt --ssh-ident=none --build --force
```

Boot the image in QEMU (`qemu-system-x86_64`), wait for `Startup complete`, and run on the serial console:

```sh
uname -a
pidin info
/data/home/root/asce_safety_core
```

*(Or copy over SSH with `scp build/x86_64/asce_safety_core root@<QEMU_IP>:/tmp/` if bridged networking is configured.)*

## Measured QNX OS 8.0 Execution & Benchmark Output (QEMU x86_64 TCG)

Measured inside QEMU 9.0.2 (`qemu-system-x86_64`, TCG software emulation on Windows 11 ARM64 / WSL2) running QNX SDP 8.0.0 (`2026/10/30-09:10:05EDT x86pc x86_64`):

```text
# uname -a
QNX noname 8.0.0 2026/10/30-09:10:05EDT x86pc x86_64
# pidin info
CPU:X86_64 Release:8.0.0  FreeMem:871MB/1023MB BootTime:Nov 18 23:07:01 UTC 2026
Processes: 17, Threads: 107
Processor1: 686 AMD 686 F6M6S3 1000MHz FPU
Processor2: 686 AMD 686 F6M6S3 1000MHz FPU
# /data/home/root/asce_safety_core
======================================================================
 ASCE TECHNOLOGIES LLC - DETERMINISTIC CYBER-PHYSICAL SAFETY CORE
 IPC Backend: QNX OS 8.0 native message passing (ChannelCreate/ConnectAttach/MsgSend/MsgReceive/MsgReply)
======================================================================
[ARBITER pid=434192] Real-time scheduling active: SCHED_FIFO prio=20
[SENSOR pid=430082] Connected -> ARBITER(pid=434192, chid=1) & ACTUATOR(pid=434195, chid=1)

[Scenario: 1. Unmitigated P-4 Isolation Request (0% Bypass -> EPA Violation Intercepted)]
  Arbiter  -> APPROVED_MODIFIED (EPA_20_PSI_INTERLOCK_PRV3_BYPASS) | End-to-End IPC: 3848.44 us
  Hydraulic-> Req Bypass: 0.0% | Applied Bypass: 25.0% | St. Jude (J-42): 98.62 PSI (EPA>=20.0)
  Actuator -> executed=1 (ACTUATED_APPROVED_MODIFIED) | SHA-256: ea32b273c4f69669...

[Scenario: 2. Post-Outage Cold-Load Pickup (All 4 Loads = 89A Inrush -> Staggered)]
  Arbiter  -> APPROVED_MODIFIED (NEC_INRUSH_STAGGER_ENFORCED) | End-to-End IPC: 1501704.65 us
  Electrical-> Peak Current Bounded: 50.0 A | Stagger Steps: 4 | Total Delay: 1500 ms
  Actuator -> executed=1 (ACTUATED_APPROVED_MODIFIED) | SHA-256: 85329c28ea58d310...

[Scenario: 3. Unauthorized Load-Shed on Medical O2 Concentrator]
  Arbiter  -> REJECTED (LIFE_SAFETY_LOAD_PROTECTED) | End-to-End IPC: 1242.03 us
  Firewall -> Target Load: medical_oxygen_conc
  Actuator -> executed=0 (BLOCKED_BY_ARBITER_LIFE_SAFETY_LOAD_PROTECTED) | SHA-256: 08d630610380f8e3...

[Benchmark: 1,000 Cycles (Baseline)] 1000 cycles in 247.61 ms (4039 Hz)
  Round-Trip Arbiter IPC Latency: mean=245.39 us | p95=413.64 us | p99=820.79 us | max=2572.32 us

[Benchmark: 1,000 Cycles (Under CPU Load Contention)] 1000 cycles in 532.12 ms (1879 Hz)
  Round-Trip Arbiter IPC Latency: mean=528.04 us | p95=1354.19 us | p99=2375.90 us | max=4265.88 us

[DONE] Clean shutdown of 3-process safety loop.
```

Even under software TCG emulation with a background CPU hog running concurrently, QNX `SCHED_FIFO` arbiter round-trip latency stayed at **0.528 ms mean** (`1.35 ms` p95, `4.27 ms` max) — well within a 50 ms cyber-physical control budget.
