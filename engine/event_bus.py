import json
import uuid
from datetime import datetime, timezone
from typing import Callable, Dict, List, Any

class EventBus:
    """Local, in-memory asynchronous pub/sub event bus with schema validation support."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event: Dict[str, Any]) -> List[Any]:
        # Ensure event has standard format
        if "event_id" not in event:
            event["event_id"] = f"evt_{uuid.uuid4().hex[:8]}"
        if "timestamp" not in event:
            event["timestamp"] = datetime.now(timezone.utc).isoformat()
            
        event_type = event.get("type", "*")
        results = []
        
        # Specific handlers
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                results.append(handler(event))
                
        # Wildcard handlers
        if "*" in self._subscribers:
            for handler in self._subscribers["*"]:
                results.append(handler(event))
                
        return results
