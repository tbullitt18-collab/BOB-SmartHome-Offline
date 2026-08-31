import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

class ImmutableAuditLog:
    """
    Append-only immutable audit log for all physical smart home state changes.
    Implements cryptographic hash chaining to guarantee audit trail integrity.
    """
    
    def __init__(self, log_path: str = None):
        if log_path is None:
            log_path = str(Path(__file__).parent / "audit_trail.jsonl")
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.last_hash = self._get_latest_hash()

    def _get_latest_hash(self) -> str:
        if not self.log_path.exists():
            return "0" * 64
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    last_record = json.loads(lines[-1].strip())
                    return last_record.get("record_hash", "0" * 64)
        except Exception:
            pass
        return "0" * 64

    def log_entry(self, entry_type: str, actor: str, payload: Dict[str, Any], decision_id: str = None) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        
        record_data = {
            "timestamp": timestamp,
            "entry_type": entry_type,
            "actor": actor,
            "decision_id": decision_id,
            "payload": payload,
            "prev_hash": self.last_hash
        }
        
        # Calculate SHA256 of the record content
        raw_bytes = json.dumps(record_data, sort_keys=True).encode("utf-8")
        record_hash = hashlib.sha256(raw_bytes).hexdigest()
        
        full_record = {**record_data, "record_hash": record_hash}
        
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(full_record) + "\n")
            
        self.last_hash = record_hash
        return full_record

    def verify_integrity(self) -> bool:
        """Verifies the unbroken cryptographic chain of all audit log records."""
        if not self.log_path.exists():
            return True
        current_prev = "0" * 64
        with open(self.log_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                if not line.strip():
                    continue
                record = json.loads(line.strip())
                expected_prev = record.get("prev_hash")
                if expected_prev != current_prev:
                    return False
                
                # Check record hash
                rec_copy = dict(record)
                actual_hash = rec_copy.pop("record_hash")
                computed_hash = hashlib.sha256(json.dumps(rec_copy, sort_keys=True).encode("utf-8")).hexdigest()
                if computed_hash != actual_hash:
                    return False
                current_prev = actual_hash
        return True
