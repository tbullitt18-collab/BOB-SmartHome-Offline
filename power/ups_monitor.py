import subprocess
import time
import sys

# Constants
UPS_NAME = "ups@localhost"
BATTERY_THRESHOLD = 20.0 # Percentage
POLL_INTERVAL = 10 # Seconds

def get_ups_status():
    try:
        # Run upsc command to get UPS details
        result = subprocess.run(['upsc', UPS_NAME], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return None, None
        
        status = None
        charge = None
        
        for line in result.stdout.split('\n'):
            if line.startswith('ups.status:'):
                status = line.split(':')[1].strip()
            elif line.startswith('battery.charge:'):
                charge = float(line.split(':')[1].strip())
                
        return status, charge
    except Exception as e:
        print(f"Error querying UPS: {e}")
        return None, None

def notify(message):
    # In a real scenario, this would send an HTTP POST to HA webhook
    # For now, we print and log
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] ALERT: {message}"
    print(log_msg)
    with open("ups_monitor.log", "a") as f:
        f.write(log_msg + "\n")

def main():
    print(f"Starting UPS Monitor for {UPS_NAME}")
    on_battery_notified = False
    low_battery_notified = False
    
    while True:
        status, charge = get_ups_status()
        
        if status and charge is not None:
            # Check if on battery
            if 'OB' in status:
                if not on_battery_notified:
                    notify(f"UPS is ON BATTERY power! Current charge: {charge}%")
                    on_battery_notified = True
                
                # Check low threshold
                if charge < BATTERY_THRESHOLD and not low_battery_notified:
                    notify(f"URGENT: UPS battery below {BATTERY_THRESHOLD}% (Current: {charge}%)")
                    low_battery_notified = True
            
            # Reset notifications if online (OL)
            if 'OL' in status:
                if on_battery_notified:
                    notify("UPS power RESTORED. Back online.")
                    on_battery_notified = False
                    low_battery_notified = False
        
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    # If run in test mode (no NUT installed), exit or mock
    # Just running a mock for demonstration since we are offline
    print("Running in mock mode. Exiting.")
    # main()
