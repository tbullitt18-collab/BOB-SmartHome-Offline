import socket
import sys

NETWORK_PREFIX = "192.168.1."
# Ports: 80 (HTTP), 8080 (Alt HTTP), 8123 (Home Assistant), 1883 (MQTT), 5683 (CoAP)
TARGET_PORTS = [80, 8080, 8123, 1883, 5683]
TIMEOUT = 0.5

def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    try:
        result = sock.connect_ex((ip, port))
        return result == 0
    except Exception:
        return False
    finally:
        sock.close()

def main():
    print("Starting Local Device Offline Scan...")
    reachable_devices = {}
    
    # Scanning a small subset for demonstration (1-20), expand to 1-255 in real usage
    for i in range(1, 21):
        ip = f"{NETWORK_PREFIX}{i}"
        open_ports = []
        for port in TARGET_PORTS:
            if check_port(ip, port):
                open_ports.append(port)
        if open_ports:
            reachable_devices[ip] = open_ports
            print(f"Found active device at {ip} with open ports: {open_ports}")
    
    print("\n--- Scan Complete ---")
    if not reachable_devices:
        print("No responsive devices found.")
    else:
        for ip, ports in reachable_devices.items():
            print(f"- {ip}: {ports}")

if __name__ == "__main__":
    main()
