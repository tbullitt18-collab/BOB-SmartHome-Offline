import threading
import urllib.request
import urllib.error
import time
import json
import random
import sys
import os

API_URL = "http://localhost:8888"
RUN_DURATION = 10
NUM_THREADS = 50

stats = {
    "requests_sent": 0,
    "success": 0,
    "connection_refused": 0,
    "other_errors": 0
}
stats_lock = threading.Lock()
running = True

def print_status(msg):
    sys.stdout.write(f"\r{msg}\033[K")
    sys.stdout.flush()

def worker():
    global running
    devices = [f"device_{i}" for i in range(500)]
    while running:
        action = random.choice(["status", "toggle", "metrics", "storm"])
        url = ""
        method = "GET"
        data = None
        headers = {}
        
        try:
            if action == "status":
                url = f"{API_URL}/api/status"
            elif action == "toggle":
                url = f"{API_URL}/api/device/toggle"
                method = "POST"
                device = random.choice(devices)
                state = random.choice(["on", "off"])
                data = json.dumps({"device_id": device, "state": state}).encode("utf-8")
                headers = {"Content-Type": "application/json"}
            elif action == "metrics":
                url = f"{API_URL}/api/metrics"
                method = "POST"
                device = random.choice(devices)
                data = json.dumps({"device_id": device, "temperature": random.uniform(10, 50), "power": random.uniform(0, 1000)}).encode("utf-8")
                headers = {"Content-Type": "application/json"}
            elif action == "storm":
                url = f"{API_URL}/api/weather"
                method = "POST"
                data = json.dumps({"pressure": random.uniform(900, 950), "wind_speed": random.uniform(80, 150), "alert": "STORM"}).encode("utf-8")
                headers = {"Content-Type": "application/json"}
            
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            
            with stats_lock:
                stats["requests_sent"] += 1
            
            with urllib.request.urlopen(req, timeout=1) as response:
                response.read()
                with stats_lock:
                    stats["success"] += 1
        except urllib.error.URLError as e:
            with stats_lock:
                reason = str(e.reason)
                if "WinError 10061" in reason or "Connection refused" in reason or "timed out" in reason or "Timeout" in reason:
                    stats["connection_refused"] += 1
                else:
                    stats["other_errors"] += 1
        except Exception as e:
            with stats_lock:
                stats["other_errors"] += 1
                
        time.sleep(0.005) # Small sleep, still fast with 50 threads

def main():
    global running
    print(r"""
     _____ _                      __  __             _             
    / ____| |                    |  \/  |           | |            
   | |    | |__   __ _  ___  ___ | \  / | ___  _ __ | | _____ _   _ 
   | |    | '_ \ / _` |/ _ \/ __|| |\/| |/ _ \| '_ \| |/ / _ \ | | |
   | |____| | | | (_| | (_) \__ \| |  | | (_) | | | |   <  __/ |_| |
    \_____|_| |_|\__,_|\___/|___/|_|  |_|\___/|_| |_|_|\_\___|\__, |
                                                               __/ |
                                                              |___/ 
    """)
    print("🔥 INITIATING CHAOS MONKEY STRESS TEST 🔥")
    print(f"Target: {API_URL}")
    print(f"Duration: {RUN_DURATION} seconds")
    print(f"Threads: {NUM_THREADS}")
    print("--------------------------------------------------")
    
    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        threads.append(t)
        
    start_time = time.time()
    while time.time() - start_time < RUN_DURATION:
        elapsed = time.time() - start_time
        with stats_lock:
            reqs = stats["requests_sent"]
        print_status(f"⚡ BLASTING API... {reqs} requests sent | 🌪️ SIMULATING STORM DATA | Time: {elapsed:.1f}s")
        time.sleep(0.1)
        
    running = False
    print("\n\n🛑 STOPPING CHAOS MONKEY 🛑")
    for t in threads:
        t.join(timeout=1.0)
        
    print("\n📊 STRESS TEST SUMMARY 📊")
    print("==================================================")
    print(f"Total Requests Sent: {stats['requests_sent']}")
    print(f"Successful Requests: {stats['success']}")
    print(f"Connection Refused:  {stats['connection_refused']}")
    print(f"Other Errors:        {stats['other_errors']}")
    print("==================================================")
    print("System is fully tested. Chaos monkey out! 🐒")

if __name__ == "__main__":
    main()
