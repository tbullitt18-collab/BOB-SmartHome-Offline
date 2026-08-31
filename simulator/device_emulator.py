import uuid
from datetime import datetime, timezone
from typing import Dict, Any

class DeviceEmulator:
    """Emulates local Zigbee and mesh sensors into canonical BOB normalized events."""
    
    @staticmethod
    def create_motion_event(source: str, occupied: bool = True) -> Dict[str, Any]:
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "type": "zigbee.motion.detected",
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "occupancy": occupied,
                "battery_percent": 92
            }
        }

    @staticmethod
    def create_barometric_event(pressure_hpa: float) -> Dict[str, Any]:
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "type": "sensor.barometric.reading",
            "source": "outdoor.weather_station",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "barometric_pressure": pressure_hpa,
                "unit": "hPa"
            }
        }

    @staticmethod
    def create_power_draw_event(watts: float, circuit: str = "living_room.plugs") -> Dict[str, Any]:
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "type": "power.draw.changed",
            "source": circuit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "power_draw_watts": watts,
                "voltage": 120.2
            }
        }

    @staticmethod
    def create_git_event(branch_name: str) -> Dict[str, Any]:
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "type": "dev.git.branch_switched",
            "source": "developer.workstation.git_hook",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "branch_name": branch_name,
                "branch_prefix": "feature/" if branch_name.startswith("feature/") else "main"
            }
        }

    @staticmethod
    def create_ci_event(status: str, repo: str = "BOB-SmartHome-Offline") -> Dict[str, Any]:
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "type": "dev.ci.build_status",
            "source": "ci.github_actions.webhook",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "status": status, # "passed", "failed", "running"
                "repository": repo
            }
        }

    @staticmethod
    def create_smoke_event(smoke_ppm: float) -> Dict[str, Any]:
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "type": "safety.smoke.detected",
            "source": "hallway.smoke_detector",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "smoke_density_ppm": smoke_ppm,
                "co_level_ppm": 12
            }
        }
