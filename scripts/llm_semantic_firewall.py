import json
import time

class ModbusSemanticFirewall:
    """
    Acts as the deterministic gatekeeper between the probabilistic LLM 
    and the physical 240V electrical relays.
    """
    def __init__(self):
        import sys
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass

        # Hardcoded, deterministic safety rules (The NEC/Life-Safety Policy)
        self.safety_policy = {
            "hvac_compressor": {"can_load_shed": True, "requires_stagger": True},
            "living_room_lights": {"can_load_shed": True, "requires_stagger": False},
            "medical_oxygen_concentrator": {"can_load_shed": False, "requires_stagger": False}, # NEVER TURN OFF
            "main_breaker": {"can_load_shed": False, "requires_stagger": False}
        }

    def evaluate_llm_command(self, llm_output: str) -> bool:
        """
        Takes raw JSON output from the offline LLM and verifies it against the laws of physics and safety.
        """
        print(f"\n[LLM Request] -> {llm_output}")
        try:
            command = json.loads(llm_output)
            device = command.get("target_device")
            action = command.get("action")

            # 1. Unknown Device Check
            if device not in self.safety_policy:
                print(f"❌ FIREWALL BLOCK: LLM hallucinated an unknown device '{device}'.")
                return False

            # 2. Life Safety Check
            if action == "power_off" and not self.safety_policy[device]["can_load_shed"]:
                print(f"🛑 FIREWALL BLOCK (LIFE SAFETY): LLM attempted to kill power to '{device}'. Overridden.")
                return False

            # 3. Inrush Current / Cold-Load Pickup Check
            if action == "power_on" and self.safety_policy[device]["requires_stagger"]:
                print(f"⚠️ FIREWALL INTERCEPT: '{device}' requires cold-load pickup staggering. Delaying start by 500ms...")
                time.sleep(0.5)

            print(f"✅ FIREWALL PASS: Executing physical Modbus actuation -> {action} on {device}")
            return True

        except json.JSONDecodeError:
            print("❌ FIREWALL BLOCK: LLM output was not valid JSON (Hallucination).")
            return False

if __name__ == "__main__":
    print("=== BOB Offline LLM Semantic Firewall Demo ===")
    firewall = ModbusSemanticFirewall()

    # Scenario 1: The user says "Turn off the AC to save battery"
    # The offline LLM correctly parses the intent into JSON.
    llm_good_intent = '{"action": "power_off", "target_device": "hvac_compressor", "reason": "battery preservation"}'
    firewall.evaluate_llm_command(llm_good_intent)

    # Scenario 2: The LLM hallucinates and tries to turn off medical equipment
    llm_dangerous_intent = '{"action": "power_off", "target_device": "medical_oxygen_concentrator", "reason": "save power"}'
    firewall.evaluate_llm_command(llm_dangerous_intent)

    # Scenario 3: The user says "Turn on the AC"
    llm_cold_load = '{"action": "power_on", "target_device": "hvac_compressor"}'
    firewall.evaluate_llm_command(llm_cold_load)
