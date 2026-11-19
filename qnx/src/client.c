#ifdef __QNX__
/*
 * client.c - Independent QNX client & devctl() benchmarker for /dev/asce_arbiter.
 *
 * Demonstrates zero-coupling microkernel communication: a separate client process
 * (often running unprivileged) opens /dev/asce_arbiter via POSIX namespace, sends
 * safety requests over QNX devctl() IPC, independently recomputes SHA-256 receipts,
 * and benchmarks 1,000 round-trip Resource Manager devctl() cycles.
 */
#include "asce_devctl.h"
#include "safety.h"
#include <devctl.h>
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

void compute_decision_receipt(const safety_req_t *req, const safety_rep_t *rep, char out[65]);

static long long now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static int cmp_ll(const void *a, const void *b)
{
    long long va = *(const long long *)a, vb = *(const long long *)b;
    return (va > vb) - (va < vb);
}

static int run_devctl_scenario(int fd, const char *label, const safety_req_t *req)
{
    asce_eval_ioctl_t io;
    memset(&io, 0, sizeof(io));
    io.req = *req;

    int verdict = 0;
    long long t0 = now_ns();
    int rc = devctl(fd, DCMD_ASCE_EVAL, &io, sizeof(io), &verdict);
    long long t1 = now_ns();
    if (rc != EOK) {
        fprintf(stderr, "devctl(DCMD_ASCE_EVAL) failed: %s\n", strerror(rc));
        return -1;
    }

    char expected_receipt[65];
    compute_decision_receipt(&io.req, &io.rep, expected_receipt);
    int hash_ok = (strcmp(expected_receipt, io.rep.receipt) == 0);

    printf("\n[%s]\n", label);
    printf("  ResMgr(/dev/asce_arbiter) -> %s (%s) | devctl IPC: %.2f us | seq=%llu\n",
           decision_str(io.rep.decision), reason_str(io.rep.reason),
           (t1 - t0) / 1000.0, (unsigned long long)io.arbiter_seq);
    if (req->type == MSG_HYDRAULIC) {
        printf("  Hydraulic -> Req Bypass: %.1f%% | Applied Bypass: %.1f%% | St. Jude (J-42): %.2f PSI\n",
               io.req.bypass_pct, io.rep.applied_bypass_pct, io.rep.predicted_psi);
    } else if (req->type == MSG_START_LOADS) {
        printf("  Electrical-> Peak Current Bounded: %.1f A | Stagger Steps: %d | Planned Delay: %u ms\n",
               io.rep.peak_amps, io.rep.stagger_steps, io.rep.stagger_ms);
    } else if (req->type == MSG_SHED_LOAD) {
        printf("  Firewall  -> Target Load: %s | Actuation Allowed: %d\n",
               LOADS[io.req.load_id].name, (io.rep.decision != DEC_REJECTED) ? 1 : 0);
    }
    printf("  Kernel Creds -> Caller PID=%ld UID=%lu | SHA-256 Verified=%s (%.16s...)\n",
           (long)io.client_pid, (unsigned long)io.client_uid,
           hash_ok ? "OK" : "MISMATCH", io.rep.receipt);
    return 0;
}

static void run_devctl_bench(int fd, const char *label, int ncycles)
{
    long long *lat_ns = calloc((size_t)ncycles, sizeof(long long));
    if (!lat_ns) return;

    asce_eval_ioctl_t io;
    int verdict = 0;
    long long total_t0 = now_ns();

    for (int i = 0; i < ncycles; i++) {
        memset(&io, 0, sizeof(io));
        io.req.seq = (unsigned)(1000 + i);
        if (i % 3 == 0) {
            io.req.type = MSG_HYDRAULIC;
            io.req.bypass_pct = (i % 2 == 0) ? 0.0 : 25.0;
        } else if (i % 3 == 1) {
            io.req.type = MSG_START_LOADS;
            io.req.load_mask = (1u << NUM_LOADS) - 1u;
        } else {
            io.req.type = MSG_SHED_LOAD;
            io.req.load_id = LOAD_MEDICAL_O2;
        }

        long long t0 = now_ns();
        int rc = devctl(fd, DCMD_ASCE_EVAL, &io, sizeof(io), &verdict);
        long long t1 = now_ns();
        if (rc != EOK) {
            fprintf(stderr, "bench devctl failed at %d: %s\n", i, strerror(rc));
            free(lat_ns);
            return;
        }
        lat_ns[i] = t1 - t0;
    }

    long long total_t1 = now_ns();
    qsort(lat_ns, (size_t)ncycles, sizeof(long long), cmp_ll);

    long long sum = 0;
    for (int i = 0; i < ncycles; i++) sum += lat_ns[i];
    double mean_us  = ((double)sum / ncycles) / 1000.0;
    double p95_us   = lat_ns[(int)(0.95 * (ncycles - 1))] / 1000.0;
    double p99_us   = lat_ns[(int)(0.99 * (ncycles - 1))] / 1000.0;
    double max_us   = lat_ns[ncycles - 1] / 1000.0;
    double total_ms = (total_t1 - total_t0) / 1e6;

    printf("\n[ResMgr devctl Benchmark: %s] %d cycles in %.2f ms (%.0f Hz)\n",
           label, ncycles, total_ms, (ncycles * 1000.0) / total_ms);
    printf("  /dev/asce_arbiter devctl() Latency: mean=%.2f us | p95=%.2f us | p99=%.2f us | max=%.2f us\n",
           mean_us, p95_us, p99_us, max_us);

    free(lat_ns);
}

int main(void)
{
    printf("======================================================================\n");
    printf(" ASCE CLIENT -> QNX RESOURCE MANAGER (%s)\n", ASCE_DEV_PATH);
    printf("======================================================================\n");

    int fd = open(ASCE_DEV_PATH, O_RDWR);
    if (fd < 0) {
        fprintf(stderr, "Failed to open %s: %s (is asce_arbiterd running?)\n",
                ASCE_DEV_PATH, strerror(errno));
        return 1;
    }

    safety_req_t r1 = { MSG_HYDRAULIC,   1, 0.0, 0,                    0,               0 };
    safety_req_t r2 = { MSG_START_LOADS, 2, 0.0, (1u << NUM_LOADS) - 1u, 0,             0 };
    safety_req_t r3 = { MSG_SHED_LOAD,   3, 0.0, 0,                    LOAD_MEDICAL_O2, 0 };

    run_devctl_scenario(fd, "ResMgr Scenario 1: P-4 Isolation (0% Bypass -> Overridden)", &r1);
    run_devctl_scenario(fd, "ResMgr Scenario 2: Cold-Load Pickup (89A -> 50A Stagger)",  &r2);
    run_devctl_scenario(fd, "ResMgr Scenario 3: Unauthorized Medical O2 Shed",             &r3);

    run_devctl_bench(fd, "1,000 Cycles (Baseline)", 1000);

    pid_t noise_pid = fork();
    if (noise_pid == 0) {
        volatile unsigned long acc = 0;
        for (;;) acc += 1;
    }
    run_devctl_bench(fd, "1,000 Cycles (Under CPU Load Contention)", 1000);
    kill(noise_pid, SIGKILL);
    waitpid(noise_pid, NULL, 0);

    asce_stats_t st;
    memset(&st, 0, sizeof(st));
    int rc = devctl(fd, DCMD_ASCE_STATS, &st, sizeof(st), NULL);
    if (rc == EOK) {
        printf("\n[Arbiter Service Telemetry via DCMD_ASCE_STATS]\n");
        printf("  daemon_pid=%ld uid=%lu gid=%lu sched=%s(%d) abilities_locked=%d watchdog_pulses=%llu\n",
               (long)st.daemon_pid, (unsigned long)st.daemon_uid, (unsigned long)st.daemon_gid,
               (st.sched_policy == SCHED_FIFO) ? "SCHED_FIFO" : "OTHER", st.sched_prio,
               st.abilities_locked, (unsigned long long)st.watchdog_pulses);
        printf("  totals: evals=%llu approved=%llu modified=%llu rejected=%llu\n",
               (unsigned long long)st.total_evals, (unsigned long long)st.approved_count,
               (unsigned long long)st.modified_count, (unsigned long long)st.rejected_count);
    }

    close(fd);
    return 0;
}
#else
int main(void) { return 0; }
#endif
