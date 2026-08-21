import json
from datetime import datetime
import os

class AuditLogger:
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.log_file = os.path.join(self.log_dir, "audit_history.json")
        
    def log_invocation(self, invocation_data: dict):
        """
        Records the internal pipeline state:
        - Trigger Timestamp
        - Input KPI Anomaly Vectors
        - Generated DAG Matrix Edges
        - Retrieved Unstructured Document IDs
        - Output Confidence Score
        - Token usage & Latency
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            **invocation_data
        }
        
        # In a production system, this would write to a proper audit DB or log stream.
        # For the prototype, we append to a local JSON file.
        existing_data = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
                
        existing_data.append(entry)
        
        with open(self.log_file, "w") as f:
            json.dump(existing_data, f, indent=2)
            
    def get_logs(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                return json.load(f)
        return []

audit_logger = AuditLogger()
