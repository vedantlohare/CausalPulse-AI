from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np
import time
from pathlib import Path

from app.engines.anomaly_detector import anomaly_detector
from app.engines.causal_graph import causal_graph
from app.engines.rag_synthesizer import rag_synthesizer
from app.engines.ambiguity_handler import ambiguity_handler
from app.engines.financial_quantifier import financial_quantifier
from app.engines.guardrails_rbac import guardrails
from app.engines.attribution_engine import attribution_engine
from app.core.gemini_client import gemini_client
from app.core.audit_logger import audit_logger
from app.core.feedback_processor import feedback_processor

router = APIRouter()

class FeedbackRequest(BaseModel):
    incident_id: str
    suggested_root_cause: str
    user_verdict: str
    user_override_node: Optional[str] = None
    comments: Optional[str] = ""


class DiagnosticRequest(BaseModel):
    role: str = "analyst"
    time_window_hours: int = 24
    scenario: str = "Steady State Baseline"
    
class LeverSimulationRequest(BaseModel):
    lever_name: str

def generate_telemetry_df(scenario: str, window_hours: int) -> pd.DataFrame:
    if "New Product Launch" in scenario:
        n = 12 # Less than 24h history
    else:
        n = 100 + window_hours
        
    end_time = pd.Timestamp.now().round("h")
    dates = pd.date_range(end=end_time, periods=n, freq="h")
    
    redis_hit_rate = np.random.normal(0.95, 0.02, n)
    db_query_time = np.random.normal(45, 5, n)
    api_latency = db_query_time + np.random.normal(20, 2, n)
    checkout_success = np.random.normal(0.99, 0.005, n)
    revenue = np.random.normal(50000, 2000, n)
    
    anomaly_len = min(12, max(2, window_hours // 4))
    anomaly_idx = slice(-anomaly_len, None)
    
    if "Outage Incident" in scenario:
        redis_hit_rate[anomaly_idx] -= np.random.uniform(0.3, 0.5, anomaly_len)
        db_query_time[anomaly_idx] += np.random.uniform(200, 400, anomaly_len)
        api_latency[anomaly_idx] += np.random.uniform(250, 500, anomaly_len)
        checkout_success[anomaly_idx] -= np.random.uniform(0.15, 0.30, anomaly_len)
        revenue[anomaly_idx] -= np.random.uniform(15000, 25000, anomaly_len)
    elif "Payment Gateway" in scenario:
        checkout_success[anomaly_idx] -= np.random.uniform(0.2, 0.4, anomaly_len)
        revenue[anomaly_idx] -= np.random.uniform(10000, 20000, anomaly_len)
    elif "Flash Sale Traffic Surge" in scenario:
        db_query_time[anomaly_idx] += np.random.uniform(100, 200, anomaly_len)
        api_latency[anomaly_idx] += np.random.uniform(150, 300, anomaly_len)
        checkout_success[anomaly_idx] -= np.random.uniform(0.05, 0.15, anomaly_len)
        revenue[anomaly_idx] += np.random.uniform(30000, 50000, anomaly_len)
    elif "Multi-Factor" in scenario:
        # DB contention + third-party gateway fail
        db_query_time[anomaly_idx] += np.random.uniform(100, 200, anomaly_len)
        api_latency[anomaly_idx] += np.random.uniform(150, 300, anomaly_len)
        checkout_success[anomaly_idx] -= np.random.uniform(0.3, 0.5, anomaly_len)
        revenue[anomaly_idx] -= np.random.uniform(20000, 40000, anomaly_len)
    elif "Ambiguous Signal" in scenario:
        revenue[anomaly_idx] -= np.random.uniform(15000, 25000, anomaly_len)
    elif "New Product Launch" in scenario:
        # Minor drop, but main issue is lack of history
        revenue[anomaly_idx] -= np.random.uniform(5000, 10000, anomaly_len)

    df = pd.DataFrame({
        "timestamp": dates,
        "region": ["US-East"] * n,
        "redis_hit_rate": np.clip(redis_hit_rate, 0, 1),
        "db_query_time_ms": db_query_time,
        "api_latency_ms": api_latency,
        "checkout_success_rate": np.clip(checkout_success, 0, 1),
        "hourly_revenue_usd": revenue
    })
    return df


@router.post("/run-diagnostics")
async def run_diagnostics(req: DiagnosticRequest):
    start_time = time.time()
    latency_breakdown = {}
    
    # 1. Anomaly Detection (Stats)
    t0 = time.time()
    df = generate_telemetry_df(req.scenario, window_hours=req.time_window_hours)
    anomalies = anomaly_detector.get_latest_anomalies(df, window_hours=req.time_window_hours)
    latency_breakdown["Stats Engine"] = round((time.time() - t0) * 1000, 2)
    
    if not anomalies:
        return {
            "status": "healthy",
            "message": "No statistical anomalies detected in the current telemetry window. All KPI Z-scores remain within normal thresholds (|Z| <= 3.0).",
            "executive_summary": f"✅ System operating normally. All metric baselines are stable across regions and services for the {req.role} persona. No revenue leakage or infrastructure bottlenecks detected.",
            "diagnostics": {
                "root_causes": [],
                "anomalies": {},
                "financial_impact": {}
            },
            "ambiguity_analysis": {
                "is_ambiguous": False,
                "confidence_score": 1.0,
                "reason": "All operational metrics within standard baseline boundaries.",
                "hypothesis_tree": [],
                "recommended_queries": []
            },
            "evidence": {
                "rag_context": []
            }
        }
        
    # 2. Causal Attribution (Engine 1)
    t0 = time.time()
    root_causes = causal_graph.trace_root_cause(anomalies)
    latency_breakdown["DAG Traversal"] = round((time.time() - t0) * 1000, 2)
    
    # 3. Contextual Retrieval (Engine 2)
    t0 = time.time()
    rag_context = []
    if root_causes:
        # Load logs if not loaded (for prototype convenience)
        rag_synthesizer.load_documents()
        
        # Build dynamic time context
        anomaly_time = anomalies[root_causes[0]]['timestamp']
        time_context = f"around {anomaly_time.strftime('%Y-%m-%d %H:%M')}"
        
        raw_context = rag_synthesizer.search_context(root_causes[0], timestamp_context=time_context)
        # Apply Guardrails (Redact PII)
        for ctx in raw_context:
            safe_text = guardrails.redact_pii(ctx['content'])
            rag_context.append({"content": safe_text, "metadata": ctx['metadata']})
            
    latency_breakdown["RAG Search"] = round((time.time() - t0) * 1000, 2)
            
    # 3.5 Attribution Scoring (Multi-Factor Evidence)
    attribution_scores = attribution_engine.score_root_causes(anomalies, root_causes, rag_context)
    
    # 4. Check Ambiguity
    ambiguity_result = ambiguity_handler.check_ambiguity(
        root_causes, 
        rag_context, 
        attribution_scores=attribution_scores, 
        history_len=len(df),
        has_anomalies=bool(anomalies)
    )
    
    # 5. Financial Quantification
    financial_impacts = {}
    for metric, data in anomalies.items():
        # Estimate based on deviation from baseline
        delta = data['value'] - data['baseline']
        impact = financial_quantifier.quantify_impact(metric, delta, req.time_window_hours)
        if impact['financial_impact_usd'] > 0:
            # RBAC Entitlement Enforcement for Financials
            val = impact['financial_impact_usd']
            if req.role == "Ops_Lead":
                if val > 5000000:
                    impact['financial_impact_display'] = "> $5M Range (Bucketed)"
                elif val > 1000000:
                    impact['financial_impact_display'] = "$1M - $5M Range (Bucketed)"
                else:
                    impact['financial_impact_display'] = "< $1M Range (Bucketed)"
            else:
                impact['financial_impact_display'] = f"-${val:,.2f}"
            
            financial_impacts[metric] = impact
            
    # 5.5 Materiality Assessment
    total_financial_loss = sum(imp['financial_impact_usd'] for imp in financial_impacts.values())
    if total_financial_loss > 1000000:
        materiality = "HIGH"
    elif total_financial_loss > 100000:
        materiality = "MEDIUM"
    else:
        materiality = "LOW"
        
    materiality_assessment = {
        "rating": materiality,
        "total_financial_exposure_usd": total_financial_loss,
        "affected_kpis": len(financial_impacts),
        "duration_hours": max([data['timestamp'].hour for data in anomalies.values()] + [0]) # simplistic duration mock
    }
            
    # 5.75 Temporal Waterfall
    temporal_waterfall = []
    if anomalies:
        sorted_anomalies = sorted(anomalies.items(), key=lambda item: item[1]['timestamp'])
        for metric, data in sorted_anomalies:
            temporal_waterfall.append({
                "metric": metric,
                "timestamp": data['timestamp'].isoformat(),
                "direction": data['direction'],
                "z_score": data['z_score']
            })
            
    # 6. Narrative Generation (Executive Output Layer)
    role_prompt = guardrails.apply_role_context(req.role)
    
    prompt = f"""
    {role_prompt}
    
    System Diagnostic Report:
    - Anomalies Detected: {list(anomalies.keys())}
    - Causal Root Cause: {root_causes}
    - RAG Context (Redacted): {rag_context}
    - Ambiguity Status: {ambiguity_result}
    - Financial Impact: {financial_impacts}
    
    Write a concise, professional executive summary (max 3 paragraphs). 
    Clearly state the root cause, financial impact, and recommended action. 
    If ambiguity is high, state that hypothesis testing is needed.
    """
    
    t0 = time.time()
    executive_summary = gemini_client.generate_narrative(prompt)
    latency_breakdown["LLM Synthesis"] = round((time.time() - t0) * 1000, 2)
    
    # 7. Audit Logging
    audit_logger.log_invocation({
        "role": req.role,
        "anomalies_count": len(anomalies),
        "root_causes": root_causes,
        "confidence_score": ambiguity_result["confidence_score"],
        "financial_impact_total": sum(v['financial_impact_usd'] for v in financial_impacts.values())
    })
    
    # 8. Return Response
    return {
        "status": "success",
        "scenario_analyzed": req.scenario,
        "executive_summary": executive_summary,
        "latency_waterfall": latency_breakdown,
        "diagnostics": {
            "root_causes": root_causes,
            "attribution_scores": attribution_scores,
            "anomalies": anomalies,
            "temporal_waterfall": temporal_waterfall,
            "financial_impact": financial_impacts,
            "materiality_assessment": materiality_assessment
        },
        "ambiguity_analysis": ambiguity_result,
        "evidence": {
            "rag_context": rag_context
        }
    }
    
    # 9. Optional Local Storage (if needed for debugging)
    df.to_csv("latest_telemetry_snapshot.csv", index=False)
    
    return response

@router.get("/evaluate")
def run_evaluation():
    """Runs the 15-case synthetic benchmark."""
    from app.benchmark_runner import run_benchmark
    return run_benchmark()

@router.post("/simulate-lever")
async def simulate_lever(req: LeverSimulationRequest):
    impact = causal_graph.simulate_lever(req.lever_name)
    if "error" in impact:
        raise HTTPException(status_code=400, detail=impact["error"])
    return {"lever": req.lever_name, "simulation": impact}

@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    result = feedback_processor.record_feedback(
        incident_id=req.incident_id,
        suggested_root_cause=req.suggested_root_cause,
        user_verdict=req.user_verdict,
        user_override_node=req.user_override_node,
        comments=req.comments or ""
    )
    return result

@router.get("/audit-logs")
async def get_audit_logs():
    return audit_logger.get_logs()

