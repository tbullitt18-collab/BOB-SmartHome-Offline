import subprocess
import time
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# National Weather Service EAS Event Codes
EAS_EVENT_CODES = {
    "TOR": "Tornado Warning",
    "SVR": "Severe Thunderstorm Warning",
    "HWW": "Hurricane Warning",
    "EVI": "Evacuation Immediate"
}

class NOAAOfflineListener:
    """
    Listens to physical radio frequencies using a $20 RTL-SDR USB antenna.
    Decodes NOAA SAME (Specific Area Message Encoding) tones entirely offline.
    """
    def __init__(self, frequency="162.550M", my_fips_code="013121"):
        self.frequency = frequency
        self.my_fips_code = my_fips_code # e.g., 013121 is Fulton County, GA

    def trigger_bob_survival_mode(self, event_type):
        """Generates the intent JSON to pass to BOB's Semantic Firewall"""
        print(f"\n🚨 [BOB EMERGENCY] Initiating Offline Survival Protocol for: {event_type} 🚨")
        
        # We generate a JSON payload just like the LLM would, but bypassing it for speed
        intent = {
            "action": "trigger_scene",
            "target_device": "home_emergency_matrix",
            "commands": [
                {"device": "all_lights", "state": "red_flash"},
                {"device": "front_door_lock", "state": "unlock"},
                {"device": "ups_battery_system", "state": "reserve_power"}
            ],
            "reason": event_type
        }
        print(f"[BOB Payload Generated]: {json.dumps(intent, indent=2)}")
        print(">> Sending to Semantic Firewall for deterministic physical execution...\n")


    def listen(self):
        """
        Simulates running the rtl_fm and multimon-ng radio decoders.
        In a real environment, this runs:
        `rtl_fm -f 162.550M -M fm -s 22050 - | multimon-ng -t raw -a EAS -`
        """
        print(f"📻 Tuning physical RTL-SDR radio to {self.frequency}...")
        print(f"👂 Listening for EAS SAME tones for FIPS code {self.my_fips_code}...")
        time.sleep(2)

        # SIMULATED RADIO OUTPUT
        # SAME Header format: ZCZC-ORG-EEE-PSSCCC-PSSCCC+TTTT-JJJHHMM-LLLLLLLL-
        # ZCZC (Start) - WXR (Weather) - TOR (Tornado) - 013121 (FIPS County)
        simulated_radio_stream = [
            "Audio carrier wave detected...",
            "Static...",
            "ZCZC-WXR-SVR-013121+0030-2821600-KFFC/NWS-", # Severe Thunderstorm
            "Static...",
            "ZCZC-WXR-TOR-013121+0045-2821630-KFFC/NWS-"  # TORNADO WARNING!
        ]

        for line in simulated_radio_stream:
            print(f"[SDR Output]: {line}")
            time.sleep(1.5)

            # Look for the EAS header ZCZC
            if "ZCZC" in line:
                # Parse the EAS SAME string
                parts = line.split('-')
                if len(parts) >= 4:
                    event_code = parts[2]
                    fips_codes = parts[3].split('+')[0] 

                    event_name = EAS_EVENT_CODES.get(event_code, "Unknown Emergency")

                    if self.my_fips_code in fips_codes:
                        print(f"\n⚠️ OFFLINE RADIO INTERCEPT: {event_name} detected for our county!")
                        if event_code == "TOR":
                            self.trigger_bob_survival_mode(event_name)
                            break
                    else:
                        print(f"Info: {event_name} detected, but not for our county. Ignoring.")

if __name__ == "__main__":
    listener = NOAAOfflineListener()
    listener.listen()
