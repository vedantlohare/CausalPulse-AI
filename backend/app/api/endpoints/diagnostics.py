from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
from pathlib import Path

from app.engines.anomaly_detector import anomaly_detector
from app.engines.causal_graph import causal_graph
from app.engines.rag_synthesizer import rag_synthesizer
from app.engines.ambiguity_handler import ambiguity_handler
from app.engines.financial_quantifier import financial_quantifier
from app.engines.guardrails_rbac import guardrails
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
    
class LeverSimulationRequest(BaseModel):
    lever_name: str

def get_telemetry_df():
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    candidate_paths = [
        base_dir / "mock_data" / "enterprise_telemetry.csv",
        base_dir / "backend" / "mock_data" / "enterprise_telemetry.csv",
        Path("./mock_data/enterprise_telemetry.csv"),
        Path("./backend/mock_data/enterprise_telemetry.csv"),
        Path("./enterprise_telemetry.csv")
    ]
    for p in candidate_paths:
        if p.exists():
            return pd.read_csv(p)
    raise HTTPException(status_code=404, detail="Telemetry data not found")


@router.post("/run-diagnostics")
async def run_diagnostics(req: DiagnosticRequest):
    # 1. Ingest Structured Data & Detect Anomalies
    df = get_telemetry_df()
    anomalies = anomaly_detector.get_latest_anomalies(df, window_hours=req.time_window_hours)
    
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
    root_causes = causal_graph.trace_root_cause(anomalies)
    
    # 3. Contextual Retrieval (Engine 2)
    rag_context = []
    if root_causes:
        # Load logs if not loaded (for prototype convenience)
        rag_synthesizer.load_documents()
        raw_context = rag_synthesizer.search_context(root_causes[0])
        # Apply Guardrails (Redact PII)
        for ctx in raw_context:
            safe_text = guardrails.redact_pii(ctx['content'])
            rag_context.append({"content": safe_text, "metadata": ctx['metadata']})
            
    # 4. Check Ambiguity
    ambiguity_result = ambiguity_handler.check_ambiguity(root_causes, rag_context)
    
    # 5. Financial Quantification
    financial_impacts = {}
    for metric, data in anomalies.items():
        # Estimate based on deviation from baseline
        delta = data['value'] - data['baseline']
        impact = financial_quantifier.quantify_impact(metric, delta, req.time_window_hours)
        if impact['financial_impact_usd'] > 0:
            financial_impacts[metric] = impact
            
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
    
    executive_summary = gemini_client.generate_narrative(prompt)
    
    # 7. Audit Logging
    audit_logger.log_invocation({
        "role": req.role,
        "anomalies_count": len(anomalies),
        "root_causes": root_causes,
        "confidence_score": ambiguity_result["confidence_score"],
        "financial_impact_total": sum(v['financial_impact_usd'] for v in financial_impacts.values())
    })
    
    # 8. Return Response
    response = {
        "status": "anomaly_detected",
        "executive_summary": executive_summary,
        "diagnostics": {
            "root_causes": root_causes,
            "anomalies": anomalies,
            "financial_impact": financial_impacts
        },
        "ambiguity_analysis": ambiguity_result,
        "evidence": {
            "rag_context": rag_context
        }
    }
    
    return response

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

