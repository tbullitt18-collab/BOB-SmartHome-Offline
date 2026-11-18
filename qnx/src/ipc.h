/*
 * ipc.h - Thin IPC layer for the ASCE safety core.
 *
 * On QNX OS 8.0 (__QNX__ defined by qcc) these map 1:1 onto native
 * microkernel message passing across processes:
 *   ChannelCreate / ConnectAttach(ND_LOCAL_NODE, pid, chid, ...) /
 *   MsgSend / MsgReceive / MsgReply.
 *
 * On non-QNX POSIX hosts a shared-memory pthread shim with identical
 * send-blocks-until-reply semantics is used ONLY so the multi-process
 * safety logic can be unit-tested before deploying to QNX.
 */
#ifndef ASCE_IPC_H
#define ASCE_IPC_H

#include <stddef.h>
#include <sys/types.h>

typedef struct ipc_handle ipc_handle_t;

ipc_handle_t *ipc_bus_init(void);
void          ipc_bus_destroy(ipc_handle_t *bus);

int         ipc_channel_create(ipc_handle_t *bus);
int         ipc_connect(ipc_handle_t *bus, pid_t server_pid, int chid);
int         ipc_send(ipc_handle_t *bus, int coid, const void *smsg, size_t sbytes, void *rmsg, size_t rbytes);
int         ipc_receive(ipc_handle_t *bus, int chid, void *msg, size_t bytes); /* returns rcvid */
int         ipc_reply(ipc_handle_t *bus, int rcvid, const void *msg, size_t bytes);
const char *ipc_backend(void);

#endif
