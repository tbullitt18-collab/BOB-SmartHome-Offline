import json
import time
from pathlib import Path
from typing import List, Dict, Any
import sys

sys.path.append(str(Path(__file__).parent.parent))
from engine.pipeline import BOBPolicyEngine

class EventReplayEngine:
    """
    Deterministic Event Replay Engine for smart home CI/CD regression testing.
    Replays historic event streams against modified policies to verify exact decision reproducibility.
    """
    
    def __init__(self, engine: BOBPolicyEngine = None):
        self.engine = engine or BOBPolicyEngine()

    def record_event_stream(self, events: List[Dict[str, Any]], output_file: str):
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for evt in events:
                f.write(json.dumps(evt) + "\n")
        print(f"Recorded {len(events)} events to {output_file}")

    def replay_stream(self, input_file: str, speed_multiplier: float = 0.0) -> List[Any]:
        path = Path(input_file)
        if not path.exists():
            raise FileNotFoundError(f"Replay file not found: {input_file}")
            
        executed_traces = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                event = json.loads(line.strip())
                traces = self.engine.event_bus.publish(event)
                # Flatten traces
                for t_list in traces:
                    if isinstance(t_list, list):
                        executed_traces.extend(t_list)
                    elif t_list:
                        executed_traces.append(t_list)
                if speed_multiplier > 0:
                    time.sleep(0.05 / speed_multiplier)
                    
        return executed_traces
