import random
from typing import Dict, Any

class FaultInjector:
    """Injects real-world chaos, packet corruption, and brownout conditions for edge stress testing."""
    
    @staticmethod
    def inject_packet_drop(event: Dict[str, Any], drop_rate: float = 0.2) -> bool:
        """Returns True if the packet should be dropped to simulate RF interference."""
        return random.random() < drop_rate

    @staticmethod
    def inject_sensor_drift(event: Dict[str, Any], drift_factor: float = 0.15) -> Dict[str, Any]:
        """Corrupts sensor values to test AI anomaly detection and safety guardrails."""
        mutated = dict(event)
        if "payload" in mutated:
            payload = dict(mutated["payload"])
            for k, v in payload.items():
                if isinstance(v, (int, float)):
                    payload[k] = v * (1.0 + random.uniform(-drift_factor, drift_factor))
            mutated["payload"] = payload
        return mutated
