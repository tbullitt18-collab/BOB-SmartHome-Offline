#ifndef ASCE_SHA256_H
#define ASCE_SHA256_H
#include <stddef.h>
/* Writes 64 lowercase hex chars + NUL into out_hex (must hold 65 bytes). */
void sha256_hex(const void *data, size_t len, char out_hex[65]);
#endif
