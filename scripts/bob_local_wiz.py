import socket
import json
import time
import ctypes
from ctypes import wintypes
import uuid

UDP_PORT = 38899
IFACE_GUID = "a565fcaf-3221-470e-b549-de63e6cdff93"
HOTSPOT_BSSID = "2e:00:2a:0f:1f:44"
HOME_BSSID = "04:4e:5a:1e:c8:56"

wlanapi = ctypes.windll.wlanapi

class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]
    @classmethod
    def from_uuid(cls, u):
        return cls.from_buffer_copy(u.bytes_le)

class DOT11_SSID(ctypes.Structure):
    _fields_ = [
        ("uSSIDLength", wintypes.ULONG),
        ("ucSSID", ctypes.c_ubyte * 32),
    ]

class NDIS_OBJECT_HEADER(ctypes.Structure):
    _fields_ = [
        ("Type", ctypes.c_ubyte),
        ("Revision", ctypes.c_ubyte),
        ("Size", wintypes.USHORT),
    ]

class DOT11_BSSID_LIST(ctypes.Structure):
    _fields_ = [
        ("Header", NDIS_OBJECT_HEADER),
        ("uNumOfEntries", wintypes.ULONG),
        ("uTotalNumOfEntries", wintypes.ULONG),
        ("BSSIDs", (ctypes.c_ubyte * 6) * 1),
    ]

class WLAN_CONNECTION_PARAMETERS(ctypes.Structure):
    _fields_ = [
        ("wlanConnectionMode", ctypes.c_int),
        ("strProfile", wintypes.LPCWSTR),
        ("pDot11Ssid", ctypes.POINTER(DOT11_SSID)),
        ("pDesiredBssidList", ctypes.POINTER(DOT11_BSSID_LIST)),
        ("dot11BssType", ctypes.c_int),
        ("dwFlags", wintypes.DWORD),
    ]

def connect_to_bssid(iface_guid_str, profile_name, ssid_str, bssid_hex):
    handle = wintypes.HANDLE()
    negotiated = wintypes.DWORD()
    wlanapi.WlanOpenHandle(2, None, ctypes.byref(negotiated), ctypes.byref(handle))
    guid = GUID.from_uuid(uuid.UUID(iface_guid_str))
    ssid = DOT11_SSID()
    ssid_bytes = ssid_str.encode("ascii")
    ssid.uSSIDLength = len(ssid_bytes)
    for i, b in enumerate(ssid_bytes):
        ssid.ucSSID[i] = b
    bssid_list = DOT11_BSSID_LIST()
    bssid_list.Header.Type = 0x80
    bssid_list.Header.Revision = 1
    bssid_list.Header.Size = ctypes.sizeof(DOT11_BSSID_LIST)
    bssid_list.uNumOfEntries = 1
    bssid_list.uTotalNumOfEntries = 1
    mac_bytes = [int(x, 16) for x in bssid_hex.split(":")]
    for i in range(6):
        bssid_list.BSSIDs[0][i] = mac_bytes[i]
    params = WLAN_CONNECTION_PARAMETERS()
    params.wlanConnectionMode = 0
    params.strProfile = profile_name
    params.pDot11Ssid = ctypes.pointer(ssid)
    params.pDesiredBssidList = ctypes.pointer(bssid_list)
    params.dot11BssType = 1
    params.dwFlags = 0
    res = wlanapi.WlanConnect(handle, ctypes.byref(guid), ctypes.byref(params), None)
    wlanapi.WlanCloseHandle(handle, None)
    return res

def get_local_subnet():
    """Detect the active local IPv4 address and /24 subnet prefix."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.168.0.1", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    if local_ip.startswith("127."):
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if not ip.startswith("127."):
                local_ip = ip
                break
    prefix = ".".join(local_ip.split(".")[:3])
    return local_ip, prefix

def _scan_and_send(prefix, local_ip, state):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.4)

    payload = json.dumps({"method": "setPilot", "params": {"state": state}}).encode("utf-8")

    # Fast-path: check known DHCP lease IPs first (192.168.0.114 on hotspot, 10.0.0.178 on home router)
    fast_ip = "192.168.0.114" if prefix == "192.168.0" else "10.0.0.178"
    try:
        sock.sendto(payload, (fast_ip, UDP_PORT))
        ack, addr = sock.recvfrom(1024)
        print(f"[FAST-PATH] WiZ Relay at {addr[0]} responded immediately!")
        print(f"[SUCCESS] Hardware ACK from {addr[0]}: {ack.decode('utf-8', errors='ignore')}")
        sock.close()
        return True
    except Exception:
        pass

    probe = json.dumps({"method": "getSystemConfig", "params": {}}).encode("utf-8")
    target_ips = []

    try:
        sock.sendto(probe, (f"{prefix}.255", UDP_PORT))
    except Exception:
        pass

    for i in range(1, 255):
        ip = f"{prefix}.{i}"
        if ip != local_ip:
            try:
                sock.sendto(probe, (ip, UDP_PORT))
            except Exception:
                pass

    end_wait = time.time() + 0.6
    while time.time() < end_wait:
        try:
            data, addr = sock.recvfrom(1024)
            found_ip = addr[0]
            if found_ip not in target_ips:
                target_ips.append(found_ip)
                print(f"[DISCOVERY] Found WiZ Relay at {found_ip}: {data.decode('utf-8', errors='ignore')}")
        except Exception:
            break

    if not target_ips:
        sock.close()
        return False

    for ip in target_ips:
        print(f"[BOB AI] Sending UDP setPilot(state={state}) -> {ip}:{UDP_PORT}...")
        for _ in range(3):
            sock.sendto(payload, (ip, UDP_PORT))
            try:
                ack, addr = sock.recvfrom(1024)
                print(f"[SUCCESS] Hardware ACK from {addr[0]}: {ack.decode('utf-8', errors='ignore')}")
                break
            except Exception:
                time.sleep(0.1)
    sock.close()
    return True

def discover_and_set_wiz(state: bool):
    action_label = "RESTORING POWER (ON)" if state else "LOAD SHEDDING (OFF)"
    print("==================================================")
    print(f" [!] BOB OFFLINE SURVIVAL MODE: {action_label}")
    print("==================================================")

    local_ip, prefix = get_local_subnet()
    print(f"[SYSTEM] Active Edge Interface: {local_ip} (Subnet: {prefix}.0/24)")

    if _scan_and_send(prefix, local_ip, state):
        return

    # If on home router (10.0.0.x) and plug is on the cloned T-Mobile Hotspot (2e:00:2a:0f:1f:44),
    # automatically hop to the T-Mobile Hotspot BSSID, fire UDP, and hop back!
    if prefix == "10.0.0":
        print(f"[ROAM] Plug not on 10.0.0.x; hopping to Cloned T-Mobile Hotspot ({HOTSPOT_BSSID})...")
        try:
            connect_to_bssid(IFACE_GUID, "freewifi", "freewifi", HOTSPOT_BSSID)
            for _ in range(14):
                time.sleep(0.4)
                local_ip, prefix = get_local_subnet()
                if prefix == "192.168.0":
                    break
            print(f"[SYSTEM] Connected to T-Mobile Hotspot: {local_ip} (Subnet: {prefix}.0/24)")
            _scan_and_send(prefix, local_ip, state)
        finally:
            connect_to_bssid(IFACE_GUID, "freewifi", "freewifi", HOME_BSSID)
            time.sleep(1.5)

if __name__ == "__main__":
    discover_and_set_wiz(False)
