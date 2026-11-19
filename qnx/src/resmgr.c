#ifdef __QNX__
/*
 * resmgr.c - ASCE Deterministic Safety Arbiter as a QNX OS 8.0 Resource Manager.
 *
 * Publishes /dev/asce_arbiter into the QNX path namespace with:
 *   1. POSIX text interface (echo "bypass=0" > /dev/asce_arbiter, cat /dev/asce_arbiter)
 *   2. Deterministic binary devctl() interface (DCMD_ASCE_EVAL, DCMD_ASCE_STATS)
 *   3. Real-time SCHED_FIFO scheduling (prio 20) + CLOCK_MONOTONIC watchdog pulse timer
 *   4. Kernel-authenticated client credentials (iofunc_client_info_ext)
 *   5. Least-privilege runtime hardening (-U uid:gid + procmgr_ability deny/lock)
 */
#include "asce_devctl.h"
#include "safety.h"
#include <errno.h>
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/iofunc.h>
#include <sys/dispatch.h>
#include <sys/neutrino.h>
#include <sys/procmgr.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

/* Implemented in safety.c */
void evaluate_safety_request(const safety_req_t *req, safety_rep_t *rep);

static iofunc_attr_t   g_attr;
static asce_stats_t    g_stats;
static struct itimerspec g_wd_its;
static timer_t         g_wd_timer;

static int on_watchdog_pulse(message_context_t *ctp, int code, unsigned flags, void *handle)
{
    (void)ctp;
    (void)code;
    (void)flags;
    (void)handle;
    g_stats.watchdog_pulses++;
    return 0;
}

static void record_evaluation(const safety_req_t *req, const safety_rep_t *rep,
                              pid_t cpid, uid_t cuid)
{
    g_stats.total_evals++;
    if (rep->decision == DEC_APPROVED) {
        g_stats.approved_count++;
    } else if (rep->decision == DEC_APPROVED_MODIFIED) {
        g_stats.modified_count++;
    } else {
        g_stats.rejected_count++;
    }

    g_stats.last_client_pid = cpid;
    g_stats.last_client_uid = cuid;
    g_stats.last_decision   = rep->decision;
    g_stats.last_reason     = rep->reason;
    if (req->type == MSG_HYDRAULIC) {
        g_stats.last_psi        = rep->predicted_psi;
        g_stats.last_bypass_pct = rep->applied_bypass_pct;
    } else if (req->type == MSG_START_LOADS) {
        g_stats.last_peak_amps = rep->peak_amps;
    }
    memcpy(g_stats.last_receipt, rep->receipt, 65);
    iofunc_time_update(&g_attr);
}

static void fetch_client_creds(resmgr_context_t *ctp, int ioflag, pid_t *cpid, uid_t *cuid)
{
    *cpid = ctp->info.pid;
    *cuid = (uid_t)-1;
    struct _client_info *cinfo = NULL;
    if (iofunc_client_info_ext(ctp, ioflag, &cinfo, 0) == EOK && cinfo != NULL) {
        *cuid = cinfo->cred.euid;
        iofunc_client_info_ext_free(&cinfo);
    }
}

static int asce_io_read(resmgr_context_t *ctp, io_read_t *msg, RESMGR_OCB_T *ocb)
{
    int status = iofunc_read_verify(ctp, msg, ocb, NULL);
    if (status != EOK) {
        return status;
    }
    if ((msg->i.xtype & _IO_XTYPE_MASK) != _IO_XTYPE_NONE) {
        return ENOSYS;
    }

    static char report[768];
    int len = snprintf(
        report, sizeof(report),
        "ASCE QNX OS 8.0 Safety Arbiter (%s)\n"
        "daemon_pid=%ld uid=%lu gid=%lu sched=%s(%d) abilities_locked=%d watchdog_pulses=%llu\n"
        "evals=%llu approved=%llu modified=%llu rejected=%llu\n"
        "last_caller_pid=%ld last_caller_uid=%lu\n"
        "last_verdict=%s reason=%s\n"
        "last_hydraulic_psi=%.2f applied_bypass_pct=%.1f last_peak_amps=%.1f\n"
        "last_sha256=%s\n",
        ASCE_DEV_PATH,
        (long)g_stats.daemon_pid, (unsigned long)g_stats.daemon_uid, (unsigned long)g_stats.daemon_gid,
        (g_stats.sched_policy == SCHED_FIFO) ? "SCHED_FIFO" : "OTHER", g_stats.sched_prio,
        g_stats.abilities_locked, (unsigned long long)g_stats.watchdog_pulses,
        (unsigned long long)g_stats.total_evals, (unsigned long long)g_stats.approved_count,
        (unsigned long long)g_stats.modified_count, (unsigned long long)g_stats.rejected_count,
        (long)g_stats.last_client_pid, (unsigned long)g_stats.last_client_uid,
        decision_str(g_stats.last_decision), reason_str(g_stats.last_reason),
        g_stats.last_psi, g_stats.last_bypass_pct, g_stats.last_peak_amps,
        g_stats.last_receipt[0] ? g_stats.last_receipt : "none");

    if (len < 0) len = 0;
    if ((size_t)len >= sizeof(report)) len = sizeof(report) - 1;

    off_t nleft = (off_t)len - ocb->offset;
    if (nleft <= 0) {
        _IO_SET_READ_NBYTES(ctp, 0);
        return _RESMGR_NPARTS(0);
    }

    size_t nbytes = (size_t)nleft;
    if (nbytes > msg->i.nbytes) {
        nbytes = msg->i.nbytes;
    }

    ocb->offset += (off_t)nbytes;
    _IO_SET_READ_NBYTES(ctp, nbytes);
    return _RESMGR_PTR(ctp, report + (ocb->offset - (off_t)nbytes), nbytes);
}

static int parse_text_cmd(const char *cmd, safety_req_t *req)
{
    memset(req, 0, sizeof(*req));
    req->seq = (unsigned)(g_stats.total_evals + 1u);

    if (strncmp(cmd, "bypass=", 7) == 0) {
        req->type = MSG_HYDRAULIC;
        req->bypass_pct = strtod(cmd + 7, NULL);
        return 0;
    }
    if (strncmp(cmd, "start=all", 9) == 0) {
        req->type = MSG_START_LOADS;
        req->load_mask = (1u << NUM_LOADS) - 1u;
        return 0;
    }
    if (strncmp(cmd, "shed=", 5) == 0) {
        const char *target = cmd + 5;
        req->type = MSG_SHED_LOAD;
        req->load_id = -1;
        for (int i = 0; i < NUM_LOADS; i++) {
            size_t n = strlen(LOADS[i].name);
            if (strncmp(target, LOADS[i].name, n) == 0) {
                req->load_id = i;
                break;
            }
        }
        return 0;
    }
    return -1;
}

static int asce_io_write(resmgr_context_t *ctp, io_write_t *msg, RESMGR_OCB_T *ocb)
{
    int status = iofunc_write_verify(ctp, msg, ocb, NULL);
    if (status != EOK) {
        return status;
    }
    if ((msg->i.xtype & _IO_XTYPE_MASK) != _IO_XTYPE_NONE) {
        return ENOSYS;
    }

    char buf[128];
    size_t nget = msg->i.nbytes;
    if (nget >= sizeof(buf)) {
        return EMSGSIZE;
    }
    ssize_t got = resmgr_msgget(ctp, buf, nget, sizeof(msg->i));
    if (got < 0) {
        return errno;
    }
    buf[got] = '\0';
    while (got > 0 && (buf[got - 1] == '\n' || buf[got - 1] == '\r' || buf[got - 1] == ' ')) {
        buf[--got] = '\0';
    }

    safety_req_t req;
    if (parse_text_cmd(buf, &req) != 0) {
        return EINVAL;
    }

    pid_t cpid;
    uid_t cuid;
    fetch_client_creds(ctp, ocb->ioflag, &cpid, &cuid);

    safety_rep_t rep;
    evaluate_safety_request(&req, &rep);
    record_evaluation(&req, &rep, cpid, cuid);

    if (rep.decision == DEC_REJECTED) {
        /* Reject unsafe actuation right at the POSIX file boundary while keeping signed audit trail */
        return EACCES;
    }

    _IO_SET_WRITE_NBYTES(ctp, msg->i.nbytes);
    return EOK;
}

static int asce_io_devctl(resmgr_context_t *ctp, io_devctl_t *msg, RESMGR_OCB_T *ocb)
{
    int status = iofunc_devctl_default(ctp, msg, ocb);
    if (status != _RESMGR_DEFAULT) {
        return status;
    }

    int dcmd = msg->i.dcmd;
    if (dcmd == DCMD_ASCE_EVAL) {
        if (msg->i.nbytes < sizeof(asce_eval_ioctl_t)) {
            return EINVAL;
        }
        asce_eval_ioctl_t *payload = (asce_eval_ioctl_t *)_DEVCTL_DATA(*msg);
        pid_t cpid;
        uid_t cuid;
        fetch_client_creds(ctp, ocb->ioflag, &cpid, &cuid);

        safety_rep_t rep;
        evaluate_safety_request(&payload->req, &rep);
        record_evaluation(&payload->req, &rep, cpid, cuid);

        payload->rep         = rep;
        payload->client_pid  = cpid;
        payload->client_uid  = cuid;
        payload->arbiter_seq = g_stats.total_evals;

        memset(&msg->o, 0, sizeof(msg->o));
        msg->o.ret_val = rep.decision;
        msg->o.nbytes  = sizeof(*payload);
        return _RESMGR_PTR(ctp, &msg->o, sizeof(msg->o) + sizeof(*payload));
    }

    if (dcmd == DCMD_ASCE_STATS) {
        if (msg->i.nbytes < sizeof(asce_stats_t)) {
            return EINVAL;
        }
        asce_stats_t *out = (asce_stats_t *)_DEVCTL_DATA(*msg);
        *out = g_stats;

        memset(&msg->o, 0, sizeof(msg->o));
        msg->o.ret_val = 0;
        msg->o.nbytes  = sizeof(*out);
        return _RESMGR_PTR(ctp, &msg->o, sizeof(msg->o) + sizeof(*out));
    }

    return ENOTTY;
}

static void drop_privileges_and_lock(uid_t uid, gid_t gid, int has_uid)
{
    /* Must configure & lock kernel abilities BEFORE dropping uid=0 (each ability is bit-OR'd with ADN|AOP|AID) */
    int rc = procmgr_ability(
        0,
        PROCMGR_ADN_ROOT | PROCMGR_ADN_NONROOT | PROCMGR_AOP_DENY | PROCMGR_AOP_LOCK | PROCMGR_AID_SPAWN,
        PROCMGR_ADN_ROOT | PROCMGR_ADN_NONROOT | PROCMGR_AOP_DENY | PROCMGR_AOP_LOCK | PROCMGR_AID_FORK,
        PROCMGR_ADN_ROOT | PROCMGR_AOP_DENY | PROCMGR_AOP_LOCK | PROCMGR_AID_REBOOT,
        PROCMGR_ADN_ROOT | PROCMGR_AOP_DENY | PROCMGR_AOP_LOCK | PROCMGR_AID_PATHSPACE,
        PROCMGR_ADN_ROOT | PROCMGR_AOP_DENY | PROCMGR_AOP_LOCK | PROCMGR_AID_MEM_SPECIAL,
        PROCMGR_AID_EOL);
    if (rc != 0) {
        fprintf(stderr, "asce_arbiterd: procmgr_ability failed: %s\n", strerror(rc > 0 ? rc : errno));
    }

    if (has_uid) {
        if (setgid(gid) != 0) perror("setgid");
        if (setuid(uid) != 0) perror("setuid");
    }

    g_stats.daemon_uid       = geteuid();
    g_stats.daemon_gid       = getegid();
    g_stats.abilities_locked = (rc == 0) ? 1 : 0;
}

int main(int argc, char **argv)
{
    int daemonize = 0;
    int has_uid   = 0;
    uid_t drop_uid = 0;
    gid_t drop_gid = 0;

    int opt;
    while ((opt = getopt(argc, argv, "dU:")) != -1) {
        if (opt == 'd') {
            daemonize = 1;
        } else if (opt == 'U') {
            char *colon = strchr(optarg, ':');
            drop_uid = (uid_t)strtoul(optarg, NULL, 10);
            drop_gid = colon ? (gid_t)strtoul(colon + 1, NULL, 10) : (gid_t)drop_uid;
            has_uid = 1;
        }
    }

    if (daemonize) {
        if (procmgr_daemon(0, PROCMGR_DAEMON_NOCLOSE | PROCMGR_DAEMON_NODEVNULL) < 0) {
            perror("procmgr_daemon");
            return 1;
        }
    }
    /* Note: procmgr_daemon closes stdin/out unless PROCMGR_DAEMON_NOCLOSE; above keeps logs visible */

    memset(&g_stats, 0, sizeof(g_stats));
    g_stats.daemon_pid = getpid();
    g_stats.last_psi   = 75.0;

    /* Elevate to real-time SCHED_FIFO before dropping root */
    struct sched_param sp = { .sched_priority = 20 };
    if (sched_setscheduler(0, SCHED_FIFO, &sp) == 0) {
        g_stats.sched_policy = SCHED_FIFO;
        g_stats.sched_prio   = sp.sched_priority;
    } else {
        g_stats.sched_policy = sched_getscheduler(0);
        if (sched_getparam(0, &sp) == 0) g_stats.sched_prio = sp.sched_priority;
    }

    dispatch_t *dpp = dispatch_create();
    if (!dpp) {
        perror("dispatch_create");
        return 1;
    }

    resmgr_connect_funcs_t connect_funcs;
    resmgr_io_funcs_t      io_funcs;
    iofunc_func_init(_RESMGR_CONNECT_NFUNCS, &connect_funcs, _RESMGR_IO_NFUNCS, &io_funcs);
    iofunc_attr_init(&g_attr, S_IFCHR | 0666, 0, 0);

    io_funcs.read   = asce_io_read;
    io_funcs.write  = asce_io_write;
    io_funcs.devctl = asce_io_devctl;

    resmgr_attr_t rattr;
    memset(&rattr, 0, sizeof(rattr));
    rattr.nparts_max   = 1;
    rattr.msg_max_size = 2048;

    int res_id = resmgr_attach(dpp, &rattr, ASCE_DEV_PATH, _FTYPE_ANY, 0,
                               &connect_funcs, &io_funcs, &g_attr);
    if (res_id < 0) {
        perror("resmgr_attach");
        return 1;
    }

    /* 500 ms monotonic kernel pulse watchdog attached into the same dispatch loop */
    int pcode = pulse_attach(dpp, MSG_FLAG_ALLOC_PULSE, 0, on_watchdog_pulse, NULL);
    int scoid = message_connect(dpp, MSG_FLAG_SIDE_CHANNEL);
    if (pcode >= 0 && scoid >= 0) {
        struct sigevent ev;
        SIGEV_PULSE_INIT(&ev, scoid, 20, pcode, 0);
        if (timer_create(CLOCK_MONOTONIC, &ev, &g_wd_timer) == 0) {
            g_wd_its.it_value.tv_sec     = 0;
            g_wd_its.it_value.tv_nsec    = 500000000L;
            g_wd_its.it_interval.tv_sec  = 0;
            g_wd_its.it_interval.tv_nsec = 500000000L;
            timer_settime(g_wd_timer, 0, &g_wd_its, NULL);
        }
    }

    /* Drop privileges and lock abilities once service is bound */
    drop_privileges_and_lock(drop_uid, drop_gid, has_uid);

    dispatch_context_t *ctp = dispatch_context_alloc(dpp);
    if (!ctp) {
        perror("dispatch_context_alloc");
        return 1;
    }

    while (1) {
        ctp = dispatch_block(ctp);
        if (!ctp) {
            if (errno == EINTR) continue;
            perror("dispatch_block");
            break;
        }
        dispatch_handler(ctp);
    }

    dispatch_context_free(ctp);
    return 0;
}
#else
int main(void) { return 0; }
#endif
