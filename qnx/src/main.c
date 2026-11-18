#define _POSIX_C_SOURCE 200809L
#include "ipc.h"
#include "safety.h"
#include <errno.h>
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

/* Implemented in safety.c */
void evaluate_safety_request(const safety_req_t *req, safety_rep_t *rep);
void compute_decision_receipt(const safety_req_t *req, const safety_rep_t *rep, char out[65]);

typedef struct {
    safety_req_t req;
    safety_rep_t verdict;
} actuator_cmd_t;

typedef struct {
    int  executed;
    char status[64];
} actuator_ack_t;

static long long now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static void sleep_ms(unsigned ms)
{
    struct timespec ts = { ms / 1000u, (long)(ms % 1000u) * 1000000L };
    nanosleep(&ts, NULL);
}

static int cmp_ll(const void *a, const void *b)
{
    long long va = *(const long long *)a, vb = *(const long long *)b;
    return (va > vb) - (va < vb);
}

/* Try elevating this process to SCHED_FIFO real-time priority (succeeds as root on QNX). */
static void try_realtime_priority(const char *role, int target_prio)
{
    struct sched_param sp;
    memset(&sp, 0, sizeof(sp));
    int pmax = sched_get_priority_max(SCHED_FIFO);
    int pmin = sched_get_priority_min(SCHED_FIFO);
    if (pmax > 0 && target_prio > pmax) target_prio = pmax;
    if (pmin >= 0 && target_prio < pmin) target_prio = pmin;
    sp.sched_priority = target_prio;

    if (sched_setscheduler(0, SCHED_FIFO, &sp) == 0) {
        printf("[%s pid=%ld] Real-time scheduling active: SCHED_FIFO prio=%d\n",
               role, (long)getpid(), sp.sched_priority);
    } else {
        printf("[%s pid=%ld] Note: SCHED_FIFO prio=%d skipped (%s; run as root on QNX for RT priority)\n",
               role, (long)getpid(), sp.sched_priority, strerror(errno));
    }
    fflush(stdout);
}

/* Process 1: Safety Arbiter Server */
static void run_arbiter(ipc_handle_t *bus, int pipe_wr)
{
    try_realtime_priority("ARBITER", 20);
    int chid = ipc_channel_create(bus);
    if (chid < 0) {
        perror("arbiter ipc_channel_create");
        _exit(1);
    }
    pid_t self = getpid();
    if (write(pipe_wr, &self, sizeof(self)) < 0 || write(pipe_wr, &chid, sizeof(chid)) < 0) {
        perror("arbiter pipe write");
        _exit(1);
    }
    close(pipe_wr);

    for (;;) {
        safety_req_t req;
        int rcvid = ipc_receive(bus, chid, &req, sizeof(req));
        if (rcvid < 0) continue;
        if (req.type == MSG_SHUTDOWN) {
            safety_rep_t bye;
            memset(&bye, 0, sizeof(bye));
            ipc_reply(bus, rcvid, &bye, sizeof(bye));
            break;
        }
        safety_rep_t rep;
        evaluate_safety_request(&req, &rep);
        ipc_reply(bus, rcvid, &rep, sizeof(rep));
    }
    _exit(0);
}

/* Process 2: Actuator Server - verifies arbiter receipt & verdict before touching hardware */
static void run_actuator(ipc_handle_t *bus, int pipe_wr)
{
    int chid = ipc_channel_create(bus);
    if (chid < 0) {
        perror("actuator ipc_channel_create");
        _exit(1);
    }
    pid_t self = getpid();
    if (write(pipe_wr, &self, sizeof(self)) < 0 || write(pipe_wr, &chid, sizeof(chid)) < 0) {
        perror("actuator pipe write");
        _exit(1);
    }
    close(pipe_wr);

    for (;;) {
        actuator_cmd_t cmd;
        int rcvid = ipc_receive(bus, chid, &cmd, sizeof(cmd));
        if (rcvid < 0) continue;
        if (cmd.req.type == MSG_SHUTDOWN) {
            actuator_ack_t bye = { 1, "SHUTDOWN" };
            ipc_reply(bus, rcvid, &bye, sizeof(bye));
            break;
        }

        actuator_ack_t ack;
        memset(&ack, 0, sizeof(ack));

        /* Independent defense-in-depth receipt verification before physical execution */
        char expected_receipt[65];
        compute_decision_receipt(&cmd.req, &cmd.verdict, expected_receipt);

        if (strcmp(expected_receipt, cmd.verdict.receipt) != 0) {
            ack.executed = 0;
            snprintf(ack.status, sizeof(ack.status), "BLOCKED_INVALID_RECEIPT");
        } else if (cmd.verdict.decision == DEC_REJECTED) {
            ack.executed = 0;
            snprintf(ack.status, sizeof(ack.status), "BLOCKED_BY_ARBITER_%s", reason_str(cmd.verdict.reason));
        } else {
            if (cmd.req.execute_delays && cmd.verdict.stagger_ms > 0) {
                sleep_ms(cmd.verdict.stagger_ms);
            }
            ack.executed = 1;
            snprintf(ack.status, sizeof(ack.status), "ACTUATED_%s", decision_str(cmd.verdict.decision));
        }
        ipc_reply(bus, rcvid, &ack, sizeof(ack));
    }
    _exit(0);
}

static void dispatch_to_chain(ipc_handle_t *bus, int arb_coid, int act_coid,
                              const char *label, const safety_req_t *req)
{
    long long t0 = now_ns();
    safety_rep_t rep;
    ipc_send(bus, arb_coid, req, sizeof(*req), &rep, sizeof(rep));

    actuator_cmd_t cmd = { *req, rep };
    actuator_ack_t ack;
    ipc_send(bus, act_coid, &cmd, sizeof(cmd), &ack, sizeof(ack));
    long long t1 = now_ns();

    printf("\n[Scenario: %s]\n", label);
    printf("  Arbiter  -> %s (%s) | End-to-End IPC: %.2f us\n",
           decision_str(rep.decision), reason_str(rep.reason), (t1 - t0) / 1000.0);
    if (req->type == MSG_HYDRAULIC) {
        printf("  Hydraulic-> Req Bypass: %.1f%% | Applied Bypass: %.1f%% | St. Jude (J-42): %.2f PSI (EPA>=%.1f)\n",
               req->bypass_pct, rep.applied_bypass_pct, rep.predicted_psi, EPA_MIN_PSI);
    } else if (req->type == MSG_START_LOADS) {
        printf("  Electrical-> Peak Current Bounded: %.1f A | Stagger Steps: %d | Total Delay: %u ms\n",
               rep.peak_amps, rep.stagger_steps, rep.stagger_ms);
    } else if (req->type == MSG_SHED_LOAD) {
        printf("  Firewall -> Target Load: %s\n", LOADS[req->load_id].name);
    }
    printf("  Actuator -> executed=%d (%s) | SHA-256: %.16s...\n",
           ack.executed, ack.status, rep.receipt);
}

static void run_latency_bench(ipc_handle_t *bus, int arb_coid, const char *label, int ncycles)
{
    long long *lat_ns = calloc((size_t)ncycles, sizeof(long long));
    if (!lat_ns) return;

    safety_req_t req;
    safety_rep_t rep;
    long long total_t0 = now_ns();

    for (int i = 0; i < ncycles; i++) {
        memset(&req, 0, sizeof(req));
        req.seq = (unsigned)(100 + i);
        req.execute_delays = 0;
        if (i % 3 == 0) {
            req.type = MSG_HYDRAULIC;
            req.bypass_pct = (i % 2 == 0) ? 0.0 : 25.0;
        } else if (i % 3 == 1) {
            req.type = MSG_START_LOADS;
            req.load_mask = (1u << NUM_LOADS) - 1u;
        } else {
            req.type = MSG_SHED_LOAD;
            req.load_id = LOAD_MEDICAL_O2;
        }
        long long t0 = now_ns();
        ipc_send(bus, arb_coid, &req, sizeof(req), &rep, sizeof(rep));
        long long t1 = now_ns();
        lat_ns[i] = t1 - t0;
    }

    long long total_t1 = now_ns();
    qsort(lat_ns, (size_t)ncycles, sizeof(long long), cmp_ll);

    long long sum = 0;
    for (int i = 0; i < ncycles; i++) sum += lat_ns[i];
    double mean_us = ((double)sum / ncycles) / 1000.0;
    double p95_us  = lat_ns[(int)(0.95 * (ncycles - 1))] / 1000.0;
    double p99_us  = lat_ns[(int)(0.99 * (ncycles - 1))] / 1000.0;
    double max_us  = lat_ns[ncycles - 1] / 1000.0;
    double total_ms = (total_t1 - total_t0) / 1e6;

    printf("\n[Benchmark: %s] %d cycles in %.2f ms (%.0f Hz)\n",
           label, ncycles, total_ms, (ncycles * 1000.0) / total_ms);
    printf("  Round-Trip Arbiter IPC Latency: mean=%.2f us | p95=%.2f us | p99=%.2f us | max=%.2f us\n",
           mean_us, p95_us, p99_us, max_us);

    free(lat_ns);
}

int main(void)
{
    printf("======================================================================\n");
    printf(" ASCE TECHNOLOGIES LLC - DETERMINISTIC CYBER-PHYSICAL SAFETY CORE\n");
    printf(" IPC Backend: %s\n", ipc_backend());
    printf("======================================================================\n");
    fflush(stdout);

    ipc_handle_t *bus = ipc_bus_init();
    if (!bus) {
        fprintf(stderr, "Failed to init IPC bus\n");
        return 1;
    }

    int arb_pipe[2], act_pipe[2];
    if (pipe(arb_pipe) != 0 || pipe(act_pipe) != 0) {
        perror("pipe");
        return 1;
    }

    pid_t arbiter_pid = fork();
    if (arbiter_pid == 0) {
        close(arb_pipe[0]); close(act_pipe[0]); close(act_pipe[1]);
        run_arbiter(bus, arb_pipe[1]);
    }

    pid_t actuator_pid = fork();
    if (actuator_pid == 0) {
        close(act_pipe[0]); close(arb_pipe[0]); close(arb_pipe[1]);
        run_actuator(bus, act_pipe[1]);
    }

    close(arb_pipe[1]);
    close(act_pipe[1]);

    pid_t r_arb_pid = 0, r_act_pid = 0;
    int arb_chid = -1, act_chid = -1;
    if (read(arb_pipe[0], &r_arb_pid, sizeof(r_arb_pid)) <= 0 ||
        read(arb_pipe[0], &arb_chid, sizeof(arb_chid)) <= 0 ||
        read(act_pipe[0], &r_act_pid, sizeof(r_act_pid)) <= 0 ||
        read(act_pipe[0], &act_chid, sizeof(act_chid)) <= 0) {
        fprintf(stderr, "Failed reading channel info from child servers\n");
        return 1;
    }
    close(arb_pipe[0]);
    close(act_pipe[0]);

    printf("[SENSOR pid=%ld] Connected -> ARBITER(pid=%ld, chid=%d) & ACTUATOR(pid=%ld, chid=%d)\n",
           (long)getpid(), (long)r_arb_pid, arb_chid, (long)r_act_pid, act_chid);

    int arb_coid = ipc_connect(bus, r_arb_pid, arb_chid);
    int act_coid = ipc_connect(bus, r_act_pid, act_chid);
    if (arb_coid < 0 || act_coid < 0) {
        perror("ipc_connect");
        return 1;
    }

    /* 1. Hydraulic safety interlock demo */
    safety_req_t r1 = { MSG_HYDRAULIC, 1, 0.0, 0, 0, 1 };
    dispatch_to_chain(bus, arb_coid, act_coid,
                      "1. Unmitigated P-4 Isolation Request (0% Bypass -> EPA Violation Intercepted)", &r1);

    /* 2. Cold-load inrush governor demo */
    safety_req_t r2 = { MSG_START_LOADS, 2, 0.0, (1u << NUM_LOADS) - 1u, 0, 1 };
    dispatch_to_chain(bus, arb_coid, act_coid,
                      "2. Post-Outage Cold-Load Pickup (All 4 Loads = 89A Inrush -> Staggered)", &r2);

    /* 3. Modbus life-safety firewall demo */
    safety_req_t r3 = { MSG_SHED_LOAD, 3, 0.0, 0, LOAD_MEDICAL_O2, 0 };
    dispatch_to_chain(bus, arb_coid, act_coid,
                      "3. Unauthorized Load-Shed on Medical O2 Concentrator", &r3);

    /* 4. Uncontested 1,000-cycle IPC benchmark */
    run_latency_bench(bus, arb_coid, "1,000 Cycles (Baseline)", 1000);

    /* 5. Contested 1,000-cycle IPC benchmark with noisy lower-priority CPU worker */
    pid_t noise_pid = fork();
    if (noise_pid == 0) {
        volatile unsigned long acc = 0;
        for (;;) acc += 1;
    }
    run_latency_bench(bus, arb_coid, "1,000 Cycles (Under CPU Load Contention)", 1000);
    kill(noise_pid, 9);
    waitpid(noise_pid, NULL, 0);

    /* Shutdown arbiter and actuator cleanly */
    safety_req_t bye_req = { MSG_SHUTDOWN, 9999, 0, 0, 0, 0 };
    safety_rep_t bye_rep;
    ipc_send(bus, arb_coid, &bye_req, sizeof(bye_req), &bye_rep, sizeof(bye_rep));

    actuator_cmd_t bye_cmd = { bye_req, bye_rep };
    actuator_ack_t bye_ack;
    ipc_send(bus, act_coid, &bye_cmd, sizeof(bye_cmd), &bye_ack, sizeof(bye_ack));

    waitpid(arbiter_pid, NULL, 0);
    waitpid(actuator_pid, NULL, 0);
    ipc_bus_destroy(bus);

    printf("\n[DONE] Clean shutdown of 3-process safety loop.\n");
    return 0;
}
