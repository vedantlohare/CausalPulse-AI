class AmbiguityHandler:
    def __init__(self, confidence_threshold: float = 0.65):
        self.confidence_threshold = confidence_threshold
        
    def check_ambiguity(self, root_causes: list, rag_context: list, attribution_scores: dict = None, history_len: int = 100, has_anomalies: bool = True) -> dict:
        """
        Determines if the diagnostic result is ambiguous (low confidence).
        Calculates a mock confidence score based on the number of root causes
        and the amount of corroborating RAG context.
        """
        if history_len < 72:
            return {
                "is_ambiguous": True,
                "confidence_score": 0.1,
                "reason": "Insufficient Data: History is too sparse (< 72 hours) to establish a reliable statistical baseline.",
                "hypothesis_tree": [
                    "Hypothesis 1: The metric is experiencing high variance typical of a new product launch.",
                    "Hypothesis 2: A true anomaly exists but is mathematically masked by sparse historical data."
                ],
                "recommended_queries": [
                    "Widen the evaluation window if older data exists.",
                    "Borrow a Bayesian prior from a comparable cohort/category."
                ]
            }

        if not root_causes:
            if not has_anomalies:
                return {
                    "is_ambiguous": False,
                    "confidence_score": 1.0,
                    "reason": "All operational metrics within standard baseline boundaries.",
                    "hypothesis_tree": [],
                    "recommended_queries": []
                }
            return {
                "is_ambiguous": True,
                "confidence_score": 0.0,
                "reason": "No statistical root causes identified.",
                "next_steps": ["Run manual SQL query on raw telemetry."]
            }
            
        # If the ONLY root cause is a business metric (like revenue) and no IT systems failed,
        # it is highly ambiguous (could be marketing, competitors, external factors).
        if root_causes == ["hourly_revenue_usd"]:
            score = 0.3
        else:
            # Calculate Evidence-Backed Confidence Score
            confidence = 0.0
            evidence_breakdown = []
            
            if attribution_scores and root_causes[0] in attribution_scores:
                scores = attribution_scores[root_causes[0]]
                confidence = scores['overall_score']
                
                # Build the evidence breakdown checklist
                if scores['anomaly_strength'] > 0.8:
                    evidence_breakdown.append("✓ Strong statistical deviation")
                else:
                    evidence_breakdown.append("! Moderate statistical deviation")
                    
                if scores['temporal_precedence'] > 0.8:
                    evidence_breakdown.append("✓ Temporal precedence aligned with causal flow")
                    
                if scores['dependency_evidence'] == 1.0:
                    evidence_breakdown.append("✓ Upstream causal lineage verified in KPI contract")
                    
                if scores['operational_evidence'] > 0.5:
                    evidence_breakdown.append("✓ Corroborating operational log events detected")
                else:
                    evidence_breakdown.append("? Weak operational log corroboration")
                    
                if history_len >= 168:
                    evidence_breakdown.append("✓ Historical baseline completeness is high (1+ week)")
                else:
                    evidence_breakdown.append("! Historical baseline is short but acceptable")
                    
            else:
                confidence = 0.4
                evidence_breakdown = ["? Insufficient data to calculate evidence score"]
                
            is_ambiguous = confidence < self.confidence_threshold
            
            return {
                "is_ambiguous": is_ambiguous,
                "confidence_score": round(confidence, 2),
                "evidence_breakdown": evidence_breakdown,
                "reason": "Root cause identified with high confidence." if not is_ambiguous else "Multiple conflicting or weak signals detected.",
                "hypothesis_tree": [
                    "Hypothesis 1: Transient network jitter affecting telemetry.",
                    "Hypothesis 2: External third-party API timeout."
                ] if is_ambiguous else [],
                "recommended_queries": [
                    "SELECT * FROM logs WHERE event_type = 'timeout';"
                ] if is_ambiguous else []
            }
        
        score = min(max(score, 0.0), 1.0) # Clamp between 0 and 1
        
        is_ambiguous = score < self.confidence_threshold
        
        result = {
            "is_ambiguous": is_ambiguous,
            "confidence_score": round(score, 2),
            "evidence_breakdown": ["! Solely a business metric drop", "? No infrastructure or IT anomalies detected upstream"]
        }
        
        if is_ambiguous:
            result["reason"] = "Confidence score below threshold (0.65). Evidence is contradictory or insufficient."
            result["hypothesis_tree"] = [
                "Hypothesis 1: The metric change is driven by external business factors (e.g., marketing, seasonality).",
                "Hypothesis 2: An upstream operational system failed but lacks telemetry coverage."
            ]
            result["recommended_queries"] = [
                "Verify external API changes or marketing campaigns.",
                "Check regional macro factors."
            ]
        else:
            result["reason"] = "Diagnostic signal is clear."
            result["hypothesis_tree"] = []
            result["recommended_queries"] = []
            
        return result

ambiguity_handler = AmbiguityHandler()
