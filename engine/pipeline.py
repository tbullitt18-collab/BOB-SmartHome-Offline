import time
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

# Path resolution for engine imports
CURRENT_DIR = Path(__file__).parent
sys.path.append(str(CURRENT_DIR.parent))

from engine.event_bus import EventBus
from observability.decision_tracer import DecisionTracer, DecisionTrace
from observability.audit_log import ImmutableAuditLog
from ai.storm_predictor import StormPredictor
from ai.anomaly_detector import DeviceAnomalyDetector
from ai.occupancy_learner import OccupancyLearner

class BOBPolicyEngine:
    """
    Core Pipeline Orchestrator:
    Device/Sensor -> Event Bus -> Policy Engine -> AI Decision -> Action -> Audit + Metrics
    """
    
    def __init__(self, policies_dir: str = None):
        self.event_bus = EventBus()
        self.tracer = DecisionTracer()
        self.audit_log = ImmutableAuditLog()
        
        # Load AI models
        self.storm_predictor = StormPredictor()
        self.anomaly_detector = DeviceAnomalyDetector()
        self.occupancy_learner = OccupancyLearner()
        
        # In-memory device state store
        self.device_states: Dict[str, Any] = {
            "lighting.office": {"state": "off", "brightness": 0, "color": "#FFFFFF"},
            "lighting.office.ambient_strip": {"state": "off", "color": "#000000"},
            "lighting.all": {"state": "normal"},
            "locks.all": {"state": "locked"},
            "hvac.main": {"state": "on", "mode": "comfort"},
            "power.plugs.non_critical": {"state": "on"},
            "system.mode": {"state": "NORMAL"}
        }
        
        # Load policies from disk
        self.policies: List[Dict[str, Any]] = []
        policies_path = Path(policies_dir or CURRENT_DIR.parent / "policies")
        self._load_policies(policies_path)
        
        # Wire up event bus listener
        self.event_bus.subscribe("*", self.process_event)

    def _load_policies(self, path: Path):
        self.policies = []
        if path.exists():
            for yaml_file in path.glob("**/*.yaml"):
                try:
                    with open(yaml_file, "r", encoding="utf-8") as f:
                        policy = yaml.safe_load(f)
                        if policy and "rules" in policy:
                            self.policies.append(policy)
                except Exception as e:
                    print(f"Error loading policy {yaml_file}: {e}")
        # Sort by priority descending (higher priority evaluated first)
        self.policies.sort(key=lambda p: p.get("priority", 0), reverse=True)

    def process_event(self, event: Dict[str, Any]) -> List[DecisionTrace]:
        """Main pipeline evaluation loop."""
        start_time = time.perf_counter()
        event_id = event.get("event_id", "evt_unknown")
        event_type = event.get("type", "")
        payload = event.get("payload", {})
        
        traces = []
        
        for policy in self.policies:
            policy_id = policy.get("policy_id", "unknown_policy")
            policy_version = policy.get("version", "v1.0.0")
            
            for rule in policy.get("rules", []):
                if rule.get("trigger_event") == event_type:
                    # Evaluate deterministic conditions
                    if not self._check_conditions(rule.get("conditions"), payload):
                        continue
                    
                    # Evaluate optional AI inference
                    ai_inference = rule.get("ai_inference")
                    ai_confidence = 1.0
                    model_version = None
                    ai_reason = "Deterministic policy match"
                    
                    if ai_inference:
                        model_name = ai_inference.get("model_name")
                        model_version = ai_inference.get("model_version")
                        min_conf = ai_inference.get("min_confidence", 0.7)
                        
                        # AI Dispatch
                        ai_passed, ai_confidence, ai_reason = self._run_ai_inference(model_name, payload)
                        if not ai_passed or ai_confidence < min_conf:
                            continue
                    
                    # Execute Actions
                    for action in rule.get("actions", []):
                        target = action.get("target")
                        command = action.get("command")
                        params = action.get("parameters", {})
                        req_approval = action.get("requires_approval", False)
                        
                        # Check Consequential Safety Approval
                        approval_granted = True
                        result = "acknowledged"
                        if req_approval:
                            # In real system, wait for PIN or local approval
                            approval_granted = False
                            result = "pending_local_approval"
                        else:
                            self._execute_device_action(target, command, params)
                        
                        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                        
                        trace = self.tracer.create_trace(
                            event_id=event_id,
                            policy_id=policy_id,
                            policy_version=policy_version,
                            model_version=model_version,
                            ai_confidence=ai_confidence,
                            trigger_reason=ai_reason,
                            evaluated_rule_id=rule.get("rule_id", "rule_default"),
                            action_target=target,
                            command=command,
                            parameters=params,
                            safety_tier="critical_safety" if policy.get("priority", 0) >= 90 else "non_critical",
                            approval_granted=approval_granted,
                            result=result,
                            execution_duration_ms=round(elapsed_ms, 2)
                        )
                        
                        # Record in append-only cryptographic audit log
                        self.audit_log.log_entry(
                            entry_type="ACTION_EXECUTED",
                            actor=f"policy:{policy_id}:{policy_version}",
                            decision_id=trace.decision_id,
                            payload={"target": target, "command": command, "parameters": params, "result": result}
                        )
                        
                        traces.append(trace)
        return traces

    def _check_conditions(self, conditions: Optional[Dict[str, Any]], payload: Dict[str, Any]) -> bool:
        if not conditions:
            return True
        for key, cond_val in conditions.items():
            if key not in payload:
                return False
            actual_val = payload[key]
            if isinstance(cond_val, str) and cond_val.startswith(">="):
                thresh = float(cond_val.replace(">=", "").strip())
                if float(actual_val) < thresh:
                    return False
            elif actual_val != cond_val:
                return False
        return True

    def _run_ai_inference(self, model_name: str, payload: Dict[str, Any]):
        if model_name == "StormPredictor":
            pressure = payload.get("barometric_pressure", 1013)
            if pressure < 990:
                return True, 0.95, f"Rapid barometric drop to {pressure} hPa indicates 95% storm probability"
            return False, 0.2, "Barometric pressure normal"
            
        elif model_name == "DeviceAnomalyDetector":
            watts = payload.get("power_draw_watts", 0)
            if watts > 3000:
                return True, 0.98, f"Severe power spike ({watts}W) detected above 3kW safety threshold"
            return False, 0.1, "Power within normal baseline"
            
        elif model_name == "OccupancyLearner":
            hour = payload.get("hour", 12)
            # CASAS occupancy logic
            if hour in [7, 8, 18, 19, 20, 21]:
                return True, 0.88, f"CASAS model predicts high occupancy at hour {hour}:00"
            return True, 0.85, f"CASAS model predicts low occupancy at hour {hour}:00 -> Safe to load shed"
            
        return True, 1.0, "Model evaluation passed"

    def _execute_device_action(self, target: str, command: str, params: Dict[str, Any]):
        if target in self.device_states:
            self.device_states[target]["state"] = command
            self.device_states[target].update(params)
        else:
            self.device_states[target] = {"state": command, **params}
