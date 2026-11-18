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

- **Sensor process**: Emits hydraulic isolation requests, post-outage motor cold-load startup masks, and load-shed commands.
- **Safety-arbiter process (`SCHED_FIFO`)**:
  1. **EPA 20 PSI Hydraulic Interlock** (`MSG_HYDRAULIC`): Evaluates downstream junction `J-42` pressure using the Millbrook hydraulic model (`hydraulic_predict_psi`). Rejects or amends unmitigated closures that drop pressure below `20.0 PSI`, inserting a `25.0%` `PRV-3` bypass (`98.62 PSI`).
  2. **NEC Cold-Load Inrush Governor** (`MSG_START_LOADS`): Sequences inductive motor starts in descending excess-inrush order (`inrush - run`) separated by `500 ms` steps so peak draw stays within the `50.0 A` breaker ceiling (`89.0 A` simultaneous → `50.0 A` staggered).
  3. **Modbus Life-Safety Firewall** (`MSG_SHED_LOAD`): Deterministically rejects load-shedding targeting protected medical equipment (`medical_oxygen_conc`).
  4. **Cryptographic Receipt**: Signs every verdict with an in-process FIPS 180-4 SHA-256 digest (`sha256.c`).
- **Actuator process**: Recomputes and verifies the SHA-256 receipt and arbiter decision before applying physical stagger delays or reporting actuation.

Under `qcc` (`__QNX__`), `src/ipc.c` compiles directly against `<sys/neutrino.h>` (`ChannelCreate`, `ConnectAttach`, `MsgSend`, `MsgReceive`, `MsgReply`).

## Build & Run on QNX SDP 8.0 (QEMU x86_64)

1. Source your QNX SDP 8.0 environment:
   ```sh
   source ~/qnx800/qnxsdp-env.sh
   ```
2. Cross-compile for QNX x86_64:
   ```sh
   cd qnx
   make
   ```
   Output binary: `build/x86_64/asce_safety_core`.
3. Boot the QNX 8.0 QEMU target (Quick Start Target Image or `mkqnximage --run`), copy the binary over SCP, and execute as `root` (needed for `SCHED_FIFO` real-time priority):
   ```sh
   scp build/x86_64/asce_safety_core root@<QEMU_IP>:/tmp/
   ssh root@<QEMU_IP> /tmp/asce_safety_core
   ```

## Host Verification (Non-QNX POSIX)

A POSIX shared-memory shim (`#ifndef __QNX__` in `src/ipc.c`) lets you compile and unit-test the safety logic with `gcc`:

```sh
cd qnx
make test-host
```

*(Host test latency reflects the Linux `pthread` shim, NOT QNX microkernel IPC performance.)*

## Measured Results

- **QNX OS 8.0 (QEMU x86_64)**: *Pending execution on QNX SDP 8.0 target — will be recorded after installing QNX Everywhere.*
