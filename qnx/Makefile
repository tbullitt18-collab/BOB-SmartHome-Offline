ifeq ($(origin CC),default)
CC := qcc
endif
ARCH ?= x86_64
QCC_TARGET_aarch64le := gcc_ntoaarch64le
QCC_TARGET_x86_64    := gcc_ntox86_64
QCC_TARGET           ?= $(or $(QCC_TARGET_$(ARCH)),gcc_ntox86_64)
CFLAGS ?= -V$(QCC_TARGET) -O2 -Wall -Wextra
LDFLAGS ?=

SRCS = src/main.c src/safety.c src/sha256.c src/ipc.c
COMMON_SRCS = src/safety.c src/sha256.c
BIN_DIR = build/$(ARCH)
TARGET = $(BIN_DIR)/asce_safety_core
RESMGR = $(BIN_DIR)/asce_arbiterd
CLIENT = $(BIN_DIR)/asce_ctl

.PHONY: all host clean test-host

all: $(TARGET) $(RESMGR) $(CLIENT)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(TARGET): $(SRCS) | $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ $(SRCS) $(LDFLAGS)

$(RESMGR): src/resmgr.c $(COMMON_SRCS) src/asce_devctl.h src/safety.h | $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ src/resmgr.c $(COMMON_SRCS) $(LDFLAGS)

$(CLIENT): src/client.c $(COMMON_SRCS) src/asce_devctl.h src/safety.h | $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ src/client.c $(COMMON_SRCS) $(LDFLAGS)

# Host unit-test build on Linux/WSL (uses POSIX shm shim in ipc.c - NOT QNX IPC)
host:
	mkdir -p build/host
	gcc -O2 -Wall -Wextra -pthread -o build/host/asce_safety_core $(SRCS) -lm

test-host: host
	./build/host/asce_safety_core

clean:
	rm -rf build
