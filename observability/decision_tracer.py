import uuid
import time
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List

@dataclass
class DecisionTrace:
    decision_id: str
    event_id: str
    timestamp: str
    policy_id: str
    policy_version: str
    model_version: Optional[str]
    ai_confidence: Optional[float]
    trigger_reason: str
    evaluated_rule_id: str
    action_target: str
    command: str
    parameters: Dict[str, Any]
    safety_tier: str
    approval_granted: bool
    result: str  # e.g., "acknowledged", "blocked_safety", "overridden", "simulated"
    execution_duration_ms: float

class DecisionTracer:
    """Records and serves structured, inspectable traces of all system decisions."""
    
    def __init__(self):
        self._traces: List[DecisionTrace] = []

    def create_trace(
        self,
        event_id: str,
        policy_id: str,
        policy_version: str,
        trigger_reason: str,
        evaluated_rule_id: str,
        action_target: str,
        command: str,
        parameters: Dict[str, Any],
        safety_tier: str = "non_critical",
        model_version: Optional[str] = None,
        ai_confidence: Optional[float] = None,
        approval_granted: bool = True,
        result: str = "acknowledged",
        execution_duration_ms: float = 0.0
    ) -> DecisionTrace:
        trace = DecisionTrace(
            decision_id=f"dec_{uuid.uuid4().hex[:10]}",
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            policy_id=policy_id,
            policy_version=policy_version,
            model_version=model_version,
            ai_confidence=ai_confidence,
            trigger_reason=trigger_reason,
            evaluated_rule_id=evaluated_rule_id,
            action_target=action_target,
            command=command,
            parameters=parameters,
            safety_tier=safety_tier,
            approval_granted=approval_granted,
            result=result,
            execution_duration_ms=execution_duration_ms
        )
        self._traces.append(trace)
        return trace

    def get_recent_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [asdict(t) for t in self._traces[-limit:]]
