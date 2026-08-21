class AmbiguityHandler:
    def __init__(self, confidence_threshold: float = 0.65):
        self.confidence_threshold = confidence_threshold
        
    def check_ambiguity(self, root_causes: list, rag_context: list) -> dict:
        """
        Determines if the diagnostic result is ambiguous (low confidence).
        Calculates a mock confidence score based on the number of root causes
        and the amount of corroborating RAG context.
        """
        if not root_causes:
            return {
                "is_ambiguous": True,
                "confidence_score": 0.0,
                "reason": "No statistical root causes identified.",
                "next_steps": ["Run manual SQL query on raw telemetry."]
            }
            
        # Mock confidence calculation
        # If the ONLY root cause is a business metric (like revenue) and no IT systems failed,
        # it is highly ambiguous (could be marketing, competitors, external factors).
        if root_causes == ["hourly_revenue_usd"]:
            score = 0.3
        else:
            score = 0.5
            
            if len(root_causes) == 1:
                score += 0.3
            elif len(root_causes) > 1:
                score -= 0.2
                
            if len(rag_context) > 0:
                score += 0.1 * min(len(rag_context), 3) # Up to +0.3 for context
            
        score = min(max(score, 0.0), 1.0) # Clamp between 0 and 1
        
        is_ambiguous = score < self.confidence_threshold
        
        result = {
            "is_ambiguous": is_ambiguous,
            "confidence_score": round(score, 2)
        }
        
        if is_ambiguous:
            result["reason"] = "Confidence score below threshold (0.65). Evidence is contradictory or insufficient."
            result["hypothesis_tree"] = [
                f"Hypothesis 1: The issue originates at {root_causes[0]} but is not captured in operational logs.",
                "Hypothesis 2: External factor (e.g., Network ISP) causing simultaneous failures."
            ]
            result["recommended_queries"] = [
                f"SELECT * FROM telemetry WHERE {root_causes[0]} IS NULL;",
                "Check Datadog for cross-region network packet loss."
            ]
            
        return result

ambiguity_handler = AmbiguityHandler()
