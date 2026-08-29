import time
import random
import pandas as pd
from app.api.endpoints.diagnostics import generate_telemetry_df
from app.engines.anomaly_detector import anomaly_detector
from app.engines.causal_graph import causal_graph
from app.engines.ambiguity_handler import ambiguity_handler
from app.engines.attribution_engine import attribution_engine

def run_benchmark():
    """
    Runs 15 synthetic cases to evaluate the Attribution Engine's accuracy and the Ambiguity Handler's abstention rate.
    Returns metrics and a detailed log.
    """
    scenarios = [
        {"name": "Clear Outage - Redis Fail", "type": "Outage Incident", "expected": ["redis_hit_rate"], "should_abstain": False},
        {"name": "Clear Outage - Redis Fail 2", "type": "Outage Incident", "expected": ["redis_hit_rate"], "should_abstain": False},
        {"name": "Payment Gateway Down", "type": "Payment Gateway", "expected": ["checkout_success_rate"], "should_abstain": False},
        {"name": "Payment Gateway Intermittent", "type": "Payment Gateway", "expected": ["checkout_success_rate"], "should_abstain": False},
        {"name": "Flash Sale Spike", "type": "Flash Sale Traffic Surge", "expected": ["db_query_time_ms"], "should_abstain": False},
        {"name": "Flash Sale Spike 2", "type": "Flash Sale Traffic Surge", "expected": ["db_query_time_ms"], "should_abstain": False},
        {"name": "Multi-Factor Failure", "type": "Multi-Factor", "expected": ["db_query_time_ms", "payment_gateway_latency_ms"], "should_abstain": False},
        {"name": "Multi-Factor Failure 2", "type": "Multi-Factor", "expected": ["db_query_time_ms", "payment_gateway_latency_ms"], "should_abstain": False},
        
        # Ambiguous Cases
        {"name": "No Tech Failure, Only Revenue Drop", "type": "Ambiguous Signal", "expected": [], "should_abstain": True},
        {"name": "No Tech Failure, Only Revenue Drop 2", "type": "Ambiguous Signal", "expected": [], "should_abstain": True},
        {"name": "Sparse Data - New Product", "type": "New Product Launch", "expected": [], "should_abstain": True},
        {"name": "Sparse Data - New Product 2", "type": "New Product Launch", "expected": [], "should_abstain": True},
        
        # Baseline Cases
        {"name": "Steady State 1", "type": "Steady State Baseline", "expected": [], "should_abstain": False},
        {"name": "Steady State 2", "type": "Steady State Baseline", "expected": [], "should_abstain": False},
        {"name": "Steady State 3", "type": "Steady State Baseline", "expected": [], "should_abstain": False}
    ]
    
    results = []
    correct_attributions = 0
    correct_abstentions = 0
    start_time = time.time()
    
    for case in scenarios:
        df = generate_telemetry_df(case["type"], window_hours=24)
        
        # Run local diagnostic chain (sans LLM and RAG)
        anomalies = anomaly_detector.get_latest_anomalies(df, window_hours=24)
        root_causes = causal_graph.trace_root_cause(anomalies)
        
        # Fake empty RAG for benchmark speed
        rag_context = [] 
        
        attribution_scores = attribution_engine.score_root_causes(anomalies, root_causes, rag_context)
        
        ambiguity_result = ambiguity_handler.check_ambiguity(
            root_causes, rag_context, attribution_scores=attribution_scores, history_len=len(df), has_anomalies=bool(anomalies)
        )
        
        is_ambiguous = ambiguity_result["is_ambiguous"]
        
        # Evaluation
        case_passed = False
        
        if case["type"] == "Steady State Baseline":
            if not root_causes and not is_ambiguous:
                case_passed = True
                correct_attributions += 1
        elif case["should_abstain"]:
            if is_ambiguous:
                case_passed = True
                correct_abstentions += 1
        else:
            # Check if expected root causes were identified and it didn't falsely abstain
            if not is_ambiguous:
                if case["type"] == "Multi-Factor":
                    # Multi-Factor requires BOTH root causes to be found
                    if all(rc in root_causes for rc in case["expected"]):
                        case_passed = True
                        correct_attributions += 1
                else:
                    # Other cases require ANY of the expected root causes
                    if any(rc in case["expected"] for rc in root_causes):
                        case_passed = True
                        correct_attributions += 1
                
        results.append({
            "scenario": case["name"],
            "detected_root_causes": root_causes,
            "is_ambiguous": is_ambiguous,
            "passed": case_passed
        })
        
    total_time = time.time() - start_time
    
    # Calculate Metrics
    # True test cases (non-abstain + baseline)
    evaluable_cases = [c for c in scenarios if not c["should_abstain"]]
    abstain_cases = [c for c in scenarios if c["should_abstain"]]
    
    accuracy = (correct_attributions / len(evaluable_cases)) * 100 if evaluable_cases else 100.0
    abstention_accuracy = (correct_abstentions / len(abstain_cases)) * 100 if abstain_cases else 100.0
    
    return {
        "total_cases": len(scenarios),
        "accuracy_pct": accuracy,
        "abstention_accuracy_pct": abstention_accuracy,
        "mean_latency_ms": (total_time / len(scenarios)) * 1000,
        "details": results
    }

if __name__ == "__main__":
    import pprint
    pprint.pprint(run_benchmark())
