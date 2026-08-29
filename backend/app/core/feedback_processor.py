import json
import os
from datetime import datetime

class FeedbackProcessor:
    def __init__(self, storage_path: str = "./logs/feedback_overrides.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
    def record_feedback(self, incident_id: str, suggested_root_cause: str, user_verdict: str, user_override_node: str = None, comments: str = "") -> dict:
        """
        Captures analyst validation or overrides for offline model retraining
        and audit review.
        """
        feedback_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "incident_id": incident_id,
            "suggested_root_cause": suggested_root_cause,
            "user_verdict": user_verdict, # "APPROVED", "REJECTED", "OVERRIDDEN"
            "user_override_node": user_override_node,
            "comments": comments
        }
        
        existing = []
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    existing = json.load(f)
            except Exception:
                existing = []
                
        existing.append(feedback_entry)
        with open(self.storage_path, "w") as f:
            json.dump(existing, f, indent=2)
            
        return {"status": "success", "message": "Analyst feedback captured for offline model retraining and audit review.", "entry": feedback_entry}

feedback_processor = FeedbackProcessor()
