CC ?= qcc
CFLAGS ?= -Vgcc_ntox86_64 -O2 -Wall -Wextra
LDFLAGS ?=
ARCH ?= x86_64

SRCS = src/main.c src/safety.c src/sha256.c src/ipc.c
BIN_DIR = build/$(ARCH)
TARGET = $(BIN_DIR)/asce_safety_core

.PHONY: all host clean test-host

all: $(TARGET)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(TARGET): $(SRCS) | $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ $(SRCS) $(LDFLAGS)

# Host unit-test build on Linux/WSL (uses POSIX shm shim in ipc.c - NOT QNX IPC)
host:
	mkdir -p build/host
	gcc -O2 -Wall -Wextra -pthread -o build/host/asce_safety_core $(SRCS) -lm

test-host: host
	./build/host/asce_safety_core

clean:
	rm -rf build
