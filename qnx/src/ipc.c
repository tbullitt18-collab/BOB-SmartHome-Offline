#include "ipc.h"
#include <stdlib.h>

#ifdef __QNX__
/* ---------------- QNX OS 8.0 native message passing ---------------- */
#include <sys/neutrino.h>
#include <sys/netmgr.h>

struct ipc_handle { int unused; };

ipc_handle_t *ipc_bus_init(void) { return calloc(1, sizeof(ipc_handle_t)); }
void          ipc_bus_destroy(ipc_handle_t *b) { free(b); }

int ipc_channel_create(ipc_handle_t *b)
{
    (void)b;
    return ChannelCreate(0);
}

int ipc_connect(ipc_handle_t *b, pid_t server_pid, int chid)
{
    (void)b;
    return ConnectAttach(ND_LOCAL_NODE, server_pid, chid, _NTO_SIDE_CHANNEL, 0);
}

int ipc_send(ipc_handle_t *b, int coid, const void *s, size_t sb, void *r, size_t rb)
{
    (void)b;
    return (int)MsgSend(coid, s, sb, r, rb);
}

int ipc_receive(ipc_handle_t *b, int chid, void *m, size_t bytes)
{
    (void)b;
    return MsgReceive(chid, m, bytes, NULL);
}

int ipc_reply(ipc_handle_t *b, int rcvid, const void *m, size_t bytes)
{
    (void)b;
    return MsgReply(rcvid, 0, m, bytes);
}

const char *ipc_backend(void)
{
    return "QNX OS 8.0 native message passing (ChannelCreate/ConnectAttach/MsgSend/MsgReceive/MsgReply)";
}

#else
/* ---------------- Multi-process POSIX shm host test shim (NOT used on QNX) ---------------- */
#include <pthread.h>
#include <string.h>
#include <sys/mman.h>

#define MAX_CH  8
#define MAX_MSG 512

typedef struct {
    pthread_mutex_t m;
    pthread_cond_t  c;
    pthread_mutex_t sendlock;
    int             state; /* 0 idle, 1 request pending, 2 replied */
    unsigned char   req[MAX_MSG];
    size_t          req_len;
    unsigned char   rep[MAX_MSG];
    size_t          rep_len;
} chan_t;

struct ipc_handle {
    pthread_mutex_t lock;
    int             n;
    chan_t          ch[MAX_CH];
};

ipc_handle_t *ipc_bus_init(void)
{
    ipc_handle_t *b = mmap(NULL, sizeof(*b), PROT_READ | PROT_WRITE,
                           MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (b == MAP_FAILED) return NULL;
    memset(b, 0, sizeof(*b));
    pthread_mutexattr_t ma;
    pthread_mutexattr_init(&ma);
    pthread_mutexattr_setpshared(&ma, PTHREAD_PROCESS_SHARED);
    pthread_mutex_init(&b->lock, &ma);
    pthread_mutexattr_destroy(&ma);
    return b;
}

void ipc_bus_destroy(ipc_handle_t *b)
{
    if (b) munmap(b, sizeof(*b));
}

int ipc_channel_create(ipc_handle_t *b)
{
    pthread_mutex_lock(&b->lock);
    int id = (b->n < MAX_CH) ? b->n++ : -1;
    if (id >= 0) {
        pthread_mutexattr_t ma;
        pthread_condattr_t ca;
        pthread_mutexattr_init(&ma);
        pthread_mutexattr_setpshared(&ma, PTHREAD_PROCESS_SHARED);
        pthread_condattr_init(&ca);
        pthread_condattr_setpshared(&ca, PTHREAD_PROCESS_SHARED);
        pthread_mutex_init(&b->ch[id].m, &ma);
        pthread_cond_init(&b->ch[id].c, &ca);
        pthread_mutex_init(&b->ch[id].sendlock, &ma);
        pthread_mutexattr_destroy(&ma);
        pthread_condattr_destroy(&ca);
        b->ch[id].state = 0;
    }
    pthread_mutex_unlock(&b->lock);
    return id;
}

int ipc_connect(ipc_handle_t *b, pid_t server_pid, int chid)
{
    (void)b;
    (void)server_pid;
    return chid;
}

int ipc_send(ipc_handle_t *b, int coid, const void *s, size_t sb, void *r, size_t rb)
{
    chan_t *ch = &b->ch[coid];
    if (sb > MAX_MSG) return -1;
    pthread_mutex_lock(&ch->sendlock);
    pthread_mutex_lock(&ch->m);
    while (ch->state != 0) pthread_cond_wait(&ch->c, &ch->m);
    memcpy(ch->req, s, sb);
    ch->req_len = sb;
    ch->state = 1;
    pthread_cond_broadcast(&ch->c);
    while (ch->state != 2) pthread_cond_wait(&ch->c, &ch->m);
    memcpy(r, ch->rep, ch->rep_len < rb ? ch->rep_len : rb);
    ch->state = 0;
    pthread_cond_broadcast(&ch->c);
    pthread_mutex_unlock(&ch->m);
    pthread_mutex_unlock(&ch->sendlock);
    return 0;
}

int ipc_receive(ipc_handle_t *b, int chid, void *m, size_t bytes)
{
    chan_t *ch = &b->ch[chid];
    pthread_mutex_lock(&ch->m);
    while (ch->state != 1) pthread_cond_wait(&ch->c, &ch->m);
    memcpy(m, ch->req, ch->req_len < bytes ? ch->req_len : bytes);
    pthread_mutex_unlock(&ch->m);
    return chid;
}

int ipc_reply(ipc_handle_t *b, int rcvid, const void *m, size_t bytes)
{
    chan_t *ch = &b->ch[rcvid];
    if (bytes > MAX_MSG) return -1;
    pthread_mutex_lock(&ch->m);
    memcpy(ch->rep, m, bytes);
    ch->rep_len = bytes;
    ch->state = 2;
    pthread_cond_broadcast(&ch->c);
    pthread_mutex_unlock(&ch->m);
    return 0;
}

const char *ipc_backend(void) { return "POSIX shm/pthread host test shim (not QNX)"; }
#endif
