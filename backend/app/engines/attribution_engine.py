import math

class AttributionEngine:
    def __init__(self):
        pass

    def score_root_causes(self, anomalies: dict, root_causes: list, rag_context: list) -> dict:
        """
        Calculates a deterministic multi-factor evidence score for candidate root causes.
        """
        results = {}
        
        if not anomalies or not root_causes:
            return results

        # Find the earliest anomaly timestamp to assess temporal precedence
        timestamps = [data['timestamp'] for data in anomalies.values()]
        earliest_time = min(timestamps) if timestamps else None
        
        # Gather all text from RAG context to check operational evidence
        rag_text = " ".join([ctx['content'].lower() for ctx in rag_context])

        for candidate in root_causes:
            if candidate not in anomalies:
                continue
                
            data = anomalies[candidate]
            
            # 1. Anomaly Strength (S_anomaly)
            # Normalize Z-score to a 0-1 scale (e.g., Z=3 -> ~0.75, Z=5 -> ~0.99)
            z = abs(data['z_score'])
            # Logistic function mapped such that z=3 is 0.73, z=4 is 0.88, z=5 is 0.95
            s_anomaly = 1.0 / (1.0 + math.exp(-(z - 2.0)))
            
            # 2. Temporal Precedence (S_temporal)
            # 1.0 if it's the very first anomaly to fire, degrading slightly if it fired later.
            time_diff = (data['timestamp'] - earliest_time).total_seconds()
            if time_diff == 0:
                s_temporal = 1.0
            else:
                s_temporal = max(0.0, 1.0 - (time_diff / 3600.0)) # decays over 1 hour
                
            # 3. Dependency Evidence (S_dependency)
            # 1.0 since it was verified by the governed DAG traversal
            s_dependency = 1.0
            
            # 4. Operational Evidence (S_operational)
            # Check if the metric name or its components (e.g. 'redis') appear in logs
            metric_parts = candidate.split('_')
            hits = sum(1 for part in metric_parts if len(part) > 2 and part.lower() in rag_text)
            s_operational = min(1.0, hits * 0.4) if hits > 0 else 0.0
            
            # Overall Score
            overall = (0.30 * s_anomaly) + (0.25 * s_temporal) + (0.25 * s_dependency) + (0.20 * s_operational)
            
            results[candidate] = {
                "anomaly_strength": round(s_anomaly, 2),
                "temporal_precedence": round(s_temporal, 2),
                "dependency_evidence": round(s_dependency, 2),
                "operational_evidence": round(s_operational, 2),
                "overall_score": round(overall, 2)
            }
            
        return results

attribution_engine = AttributionEngine()
