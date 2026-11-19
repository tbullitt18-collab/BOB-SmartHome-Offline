#ifndef ASCE_DEVCTL_H
#define ASCE_DEVCTL_H

#include "safety.h"
#include <stdint.h>
#include <sys/types.h>

#define ASCE_DEV_PATH "/dev/asce_arbiter"

typedef struct {
    safety_req_t req;
    safety_rep_t rep;
    pid_t        client_pid;
    uid_t        client_uid;
    uint64_t     arbiter_seq;
} asce_eval_ioctl_t;

typedef struct {
    pid_t    daemon_pid;
    uid_t    daemon_uid;
    gid_t    daemon_gid;
    int      sched_policy;
    int      sched_prio;
    int      abilities_locked;
    uint64_t total_evals;
    uint64_t approved_count;
    uint64_t modified_count;
    uint64_t rejected_count;
    uint64_t watchdog_pulses;
    pid_t    last_client_pid;
    uid_t    last_client_uid;
    double   last_psi;
    double   last_bypass_pct;
    double   last_peak_amps;
    int      last_decision;
    int      last_reason;
    char     last_receipt[65];
} asce_stats_t;

#ifdef __QNX__
#include <devctl.h>
#define DCMD_ASCE_EVAL   __DIOTF(_DCMD_MISC, 1, asce_eval_ioctl_t)
#define DCMD_ASCE_STATS  __DIOF (_DCMD_MISC, 2, asce_stats_t)
#endif

#endif
