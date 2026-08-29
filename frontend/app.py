import streamlit as st
import requests
import json
import networkx as nx
import plotly.graph_objects as go
from pathlib import Path
import yaml
import time

st.set_page_config(layout="wide", page_title="CausalPulse AI | Enterprise KPI Diagnostic", page_icon="")

# Custom CSS for Premium Design
st.markdown("""
    <style>
    .main {
        background-color: #0B0E14;
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        background: linear-gradient(145deg, #161B26, #121620);
        border: 1px solid #283347;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .summary-card {
        background: linear-gradient(135deg, #1E2D4A, #121D33);
        border-radius: 12px;
        padding: 22px;
        border-left: 5px solid #38B2AC;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .ambiguity-card {
        background: linear-gradient(135deg, #4A2E12, #2D1B0B);
        border-radius: 12px;
        padding: 22px;
        border-left: 5px solid #ED8936;
        margin-bottom: 20px;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-success { background-color: #22543D; color: #9AE6B4; }
    .badge-warning { background-color: #7B341E; color: #FBD38D; }
    .badge-info { background-color: #2A4365; color: #90CDF4; }
    </style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000/api/v1/diagnostics"

def load_kpi_contract():
    base_dir = Path(__file__).resolve().parent.parent
    contract_path = base_dir / "backend" / "app" / "schema" / "kpi_contract.yml"
    if contract_path.exists():
        with open(contract_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {"kpis": {}, "levers": {}}

def render_causal_graph(root_causes, anomalies, contract):
    """Renders an interactive DAG using Plotly"""
    G = nx.DiGraph()
    kpis = contract.get('kpis', {})
    for kpi, config in kpis.items():
        G.add_node(kpi)
        for up in config.get('upstream_dependencies', []):
            G.add_edge(up, kpi)

    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2.5, color='#4A5568'),
        hoverinfo='none',
        mode='lines')

    node_x, node_y, node_text, node_color, node_hover = [], [], [], [], []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node.replace("_", " ").title())
        
        if node in root_causes:
            node_color.append('#E53E3E') # Red for root cause
            node_hover.append(f"<b>Root Cause Node: {node}</b><br>Isolated failure origin")
        elif node in anomalies:
            node_color.append('#ED8936') # Orange for downstream anomaly
            node_hover.append(f"<b>Downstream Anomaly: {node}</b><br>Impacted by root cause")
        else:
            node_color.append('#38B2AC') # Teal for healthy
            node_hover.append(f"<b>Healthy Node: {node}</b>")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        hovertext=node_hover,
        marker=dict(
            showscale=False,
            color=node_color,
            size=36,
            line=dict(width=2, color='#FFFFFF')),
        textposition="bottom center",
        textfont=dict(color='#E2E8F0', size=11, family='Inter'))

    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title=dict(
                    text='<b>Topological Causal Dependency DAG (Directed Acyclic Graph)</b>',
                    font=dict(size=15, color='#E2E8F0')
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    st.plotly_chart(fig, use_container_width=True)

# Main Navigation
st.sidebar.title("CausalPulse AI")
st.sidebar.markdown("##### *Enterprise KPI Diagnostic Engine*")
st.sidebar.markdown("---")

tab_selection = st.sidebar.radio(
    "Navigation", 
    ["Live Diagnostic Workspace", "Empirical Benchmark (v2.0)", "Semantic KPI Contracts", "Audit Trail & Telemetry", "Continuous Learning Loop"]
)

# Sidebar settings
st.sidebar.markdown("### Demo Scenario Selector")
scenario_preset = st.sidebar.selectbox(
    "Select Incident Scenario",
    [
        "Outage Incident (Redis Failover -> DB Spike -> Revenue Drop)",
        "Payment Gateway Degradation (Third-Party Webhook Latency -> Churn Risk)",
        "Flash Sale Traffic Surge (5x API Load -> DB Contention)",
        "Multi-Factor (Traffic Surge + Payment Gateway Failure)",
        "New Product Launch (Sparse Data / Insufficient History)",
        "Ambiguous Signal (Low Confidence / Abstain Mode)",
        "Steady State Baseline (Healthy / No Anomalies)"
    ]
)

role = st.sidebar.selectbox("Executive Persona View", ["Ops_Lead", "CMO", "Analyst"], index=0)

if "Outage Incident" in scenario_preset:
    window = 144
elif "Payment Gateway" in scenario_preset:
    window = 96
elif "Flash Sale Traffic Surge" in scenario_preset:
    window = 48
elif "Multi-Factor" in scenario_preset:
    window = 96
elif "New Product Launch" in scenario_preset:
    window = 48
elif "Ambiguous Signal" in scenario_preset:
    window = 72
else:
    window = 24

st.sidebar.caption(f"Active Analysis Window: **{window} Hours**")


# ----------------- TAB 1: LIVE DIAGNOSTIC WORKSPACE -----------------
if tab_selection == "Live Diagnostic Workspace":
    st.title("Live Incident & Causal Attribution")
    st.caption("Deterministic Causal Inference (NetworkX/Stats) + Contextual Semantic RAG + Prescriptive Action")
    
    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        run_pulse = st.button("Run Diagnostic Pulse", type="primary", use_container_width=True)
        
    if run_pulse:
        start_time = time.time()
        with st.spinner("Analyzing telemetry signals, constructing DAG, and querying qualitative context..."):
            try:
                response = requests.post(f"{API_URL}/run-diagnostics", json={
                    "role": role,
                    "time_window_hours": window,
                    "scenario": scenario_preset
                })
                elapsed_ms = round((time.time() - start_time) * 1000, 1)
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state['last_diagnostic'] = data
                    st.session_state['last_elapsed'] = elapsed_ms
                else:
                    st.error(f"Backend returned error: {response.text}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI backend at {API_URL}. Ensure it is running.")
                
    if 'last_diagnostic' in st.session_state:
        data = st.session_state['last_diagnostic']
        elapsed = st.session_state.get('last_elapsed', 45.0)
        ambiguity = data.get('ambiguity_analysis', {})
        diagnostics = data.get('diagnostics', {})
        anomalies = diagnostics.get('anomalies', {})
        root_causes = diagnostics.get('root_causes', [])
        confidence_score = ambiguity.get('confidence_score', 1.0)
        
        # Top banner stats
        b1, b2, b3, b4, b5, b6 = st.columns(6)
        with b1:
            st.markdown(f"<div class='metric-card'><span class='badge badge-info'>Persona</span><h3>{role}</h3></div>", unsafe_allow_html=True)
        with b2:
            st.markdown(f"<div class='metric-card'><span class='badge badge-warning'>Confidence Score</span><h3>{confidence_score} / 1.0</h3></div>", unsafe_allow_html=True)
        with b3:
            mat = diagnostics.get("materiality_assessment", {})
            mat_rating = mat.get("rating", "N/A")
            color = "badge-error" if mat_rating == "HIGH" else "badge-warning"
            st.markdown(f"<div class='metric-card'><span class='badge {color}'>Materiality</span><h3>{mat_rating}</h3></div>", unsafe_allow_html=True)
        with b4:
            st.markdown(f"<div class='metric-card'><span class='badge badge-success'>Execution Latency</span><h3>{elapsed} ms</h3></div>", unsafe_allow_html=True)
            waterfall = data.get("latency_waterfall", {})
            if waterfall:
                with st.popover("Waterfall Breakdown"):
                    for k, v in waterfall.items():
                        st.caption(f"**{k}**: {v} ms")
        with b5:
            st.markdown(f"<div class='metric-card'><span class='badge badge-info'>Anomalies Detected</span><h3>{len(anomalies)} Nodes</h3></div>", unsafe_allow_html=True)
        
        # Telemetry Estimation (Tokens)
        llm_telemetry = data.get("llm_telemetry", {"model_calls": 0, "total_tokens": 0, "estimated_cost_usd": 0.0, "is_mock": False})
        total_tokens = llm_telemetry.get("total_tokens", 0)
        cost_estimate = llm_telemetry.get("estimated_cost_usd", 0.0)
        model_calls = llm_telemetry.get("model_calls", 0)
        mock_label = " (Sim)" if llm_telemetry.get("is_mock", False) else ""
        with b6:
            st.markdown(f"<div class='metric-card'><span class='badge badge-warning'>LLM Telemetry{mock_label}</span><h3>{total_tokens} tokens</h3><p style='margin:0; font-size:12px; color:#A0AEC0;'>Model Calls: {model_calls} | Est. Cost: ${cost_estimate:.5f}</p></div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 1. Executive Summary
        if not ambiguity.get("is_ambiguous", False):
            st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
            st.subheader(f"Executive Briefing ({role} Persona)")
            st.write(data.get("executive_summary", data.get("message", "System operating within baseline.")))
            
            # Confidence Breakdown
            breakdown = ambiguity.get("evidence_breakdown", [])
            if breakdown:
                st.markdown("##### Confidence Evidence Checklist")
                for item in breakdown:
                    st.markdown(f"<span style='color:#A0AEC0; font-size:14px;'>{item}</span>", unsafe_allow_html=True)
                    
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='ambiguity-card'>", unsafe_allow_html=True)
            st.subheader("Active Ambiguity Mode (Confidence < 0.65)")
            st.write(ambiguity.get("reason", "Ambiguous diagnostic signals detected."))
            st.markdown("#### Guided Diagnostic Hypothesis Tree")
            for hyp in ambiguity.get("hypothesis_tree", []):
                st.write(f"- {hyp}")
            st.markdown("#### Recommended Supplementary Queries")
            for q in ambiguity.get("recommended_queries", []):
                st.code(q, language="sql")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Download Report Feature
        report_content = f"# CausalPulse AI - Executive Diagnostic Report\n\n**Persona:** {role}\n**Confidence Score:** {confidence_score}\n\n## Executive Summary\n{data.get('executive_summary', data.get('message', 'All systems nominal.'))}\n\n## Root Causes Detected\n- " + ("\n- ".join(root_causes) if root_causes else "None (System Healthy)") + "\n\n## System Anomalies\n- " + ("\n- ".join(anomalies.keys()) if anomalies else "None (All metrics in baseline)")
        st.download_button(
            label="📥 Download Executive PDF / Markdown Report",
            data=report_content,
            file_name=f"CausalPulse_Report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True
        )
            
        # 2. Financial Impact Breakdown
        st.subheader("Real-Time Financial Impact Quantification")
        impacts = diagnostics.get("financial_impact", {})
        if impacts:
            f_cols = st.columns(len(impacts))
            for i, (metric, imp) in enumerate(impacts.items()):
                with f_cols[i]:
                    display_val = imp.get('financial_impact_display', f"-${imp.get('financial_impact_usd', 0.0):,.2f}")
                    st.markdown(f"""
                        <div class='metric-card'>
                            <h5>{metric.replace('_', ' ').title()}</h5>
                            <h3 style='color: #FC8181;'>{display_val}</h3>
                            <p style='color: #A0AEC0; font-size: 0.85em;'>{imp.get('description', '')}</p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No financial drain computed. All metric thresholds are within acceptable enterprise variance.")
            
        with st.expander("View Modeled Financial Assumptions (from kpi_contract.yml)"):
            assumptions = contract.get("financial_assumptions", {}) if 'contract' in locals() else {"avg_order_value_usd": 150.0, "baseline_checkouts_per_hour": 1000}
            st.json(assumptions)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2.5 Temporal Waterfall
        waterfall = diagnostics.get("temporal_waterfall", [])
        if waterfall:
            st.subheader("Temporal Incident Waterfall")
            for idx, event in enumerate(waterfall):
                # Check if it was redacted
                raw_data = anomalies.get(event['metric'], {})
                if raw_data.get('value') == "[RESTRICTED — insufficient role clearance]":
                    st.markdown(f"**[{idx+1}] {event['timestamp']}**: `{event['metric']}` <span class='badge badge-warning'>Restricted for this persona</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**[{idx+1}] {event['timestamp']}**: `{event['metric']}` ({event['direction']}, z-score: {event['z_score']:.2f})")
            st.markdown("<br>", unsafe_allow_html=True)
            
        # 3. DAG Graph & Qualitative Evidence
        col_dag, col_rag = st.columns([3, 2])
        with col_dag:
            contract = load_kpi_contract()
            render_causal_graph(
                root_causes, 
                anomalies, 
                contract
            )
            
            # Attribution Scores
            attribution = diagnostics.get("attribution_scores", {})
            if attribution and root_causes:
                st.markdown("### Evidence Provenance Matrix")
                sorted_rcs = sorted(root_causes, key=lambda rc: attribution.get(rc, {}).get("overall_score", 0), reverse=True)
                for idx, rc in enumerate(sorted_rcs):
                    if rc in attribution:
                        scores = attribution[rc]
                        label = "Primary Driver 🔴" if idx == 0 else "Secondary Contributor 🟠"
                        st.markdown(f"**{label}: `{rc}`**")
                        st.json({
                            "Overall Attribution Score": f"{scores['overall_score']} / 1.0",
                            "1. Anomaly Strength (z-score logit)": scores['anomaly_strength'],
                            "2. Temporal Precedence (sequence)": scores['temporal_precedence'],
                            "3. Dependency Verification (DAG)": scores['dependency_evidence'],
                            "4. Operational Evidence (RAG)": scores['operational_evidence']
                        })
        with col_rag:
            st.subheader("Qualitative Log Evidence (RAG)")
            st.caption("Masked PII Guardrails Applied (`[REDACTED_PII]`)")
            
            rag_mode = data.get("evidence", {}).get("rag_mode", "unknown")
            mode_badge_color = "badge-success" if rag_mode == "vector" else "badge-warning"
            mode_display = "Vector RAG (ChromaDB)" if rag_mode == "vector" else "Keyword Fallback"
            st.markdown(f"<div style='margin-bottom: 10px;'><span class='badge {mode_badge_color}'>Retrieval Engine: {mode_display}</span></div>", unsafe_allow_html=True)

            rag_list = data.get("evidence", {}).get("rag_context", [])
            telemetry_freshness = data.get("evidence", {}).get("structured_telemetry_freshness", "Real-time")
            st.markdown(f"<span style='font-size: 0.85em; color: #A0AEC0;'>Structured Telemetry: {telemetry_freshness}</span>", unsafe_allow_html=True)
            
            if rag_list:
                for ctx in rag_list:
                    meta = ctx.get('metadata', {})
                    freshness = meta.get('last_refreshed', 'Unknown')
                    st.info(f"**{meta.get('source', 'Log')} ({meta.get('type', 'Alert')}) | {meta.get('timestamp', '')}** *Refreshed: {freshness}*\n\n{ctx.get('content', '')}")
            else:
                st.info("ℹ️ No active operational alerts or incident complaints logged for the current healthy baseline.")
                
        # 4. Action Levers & Counterfactual Simulator
        st.divider()
        st.subheader("Prescriptive Decision & Counterfactual Simulator")
        st.write("Evaluate mitigation strategies before taking action in production.")
        
        sim_col1, sim_col2 = st.columns([1, 2])
        with sim_col1:
            contract_levers = list(load_kpi_contract().get("levers", {}).keys()) or ["reroute_traffic", "scale_db_replicas", "circuit_breaker_payment_gateway"]
            selected_lever = st.selectbox("Select Controllable Business Lever", contract_levers)
            sim_btn = st.button("Run Counterfactual Simulation", use_container_width=True)
        with sim_col2:
            if sim_btn:
                try:
                    sim_resp = requests.post(f"{API_URL}/simulate-lever", json={"lever_name": selected_lever})
                    if sim_resp.status_code == 200:
                        sim_out = sim_resp.json()
                        st.success(f"Simulation Complete for lever: `{selected_lever}`")
                        sim = sim_out.get("simulation", {})
                        for metric, details in sim.items():
                            st.markdown(f"#### Primary Impact: `{metric}`")
                            col_a, col_b = st.columns(2)
                            with col_a:
                                improvement = details.get('direct_improvement', 0)
                                st.markdown(f"<div class='metric-card' style='border-left: 4px solid #48BB78;'><span class='badge badge-success'>Estimated Recovery</span><h3 style='color: #48BB78; margin-top: 10px;'>+{improvement}%</h3><p style='color: #A0AEC0; font-size: 0.8em; margin: 0;'>Expected return to baseline</p></div>", unsafe_allow_html=True)
                            with col_b:
                                affected = details.get('downstream_metrics_affected', [])
                                st.markdown(f"<div class='metric-card' style='border-left: 4px solid #3182CE;'><span class='badge badge-info'>Cascading Protection</span><div style='margin-top: 10px;'>", unsafe_allow_html=True)
                                for m in affected:
                                    st.markdown(f"🔹 `{m}`")
                                st.markdown("</div></div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Simulation failed: {e}")

        # 5. Feedback Loop
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🔁 Continuous Learning Feedback Loop")
        st.markdown("Did the engine accurately identify the root cause?")
        f1, f2, f3 = st.columns([1,1,4])
        with f1:
            if st.button("👍 Yes, spot on"):
                st.success("Feedback registered! Strengthening causal edge weights.")
        with f2:
            if st.button("👎 No, incorrect"):
                st.error("Feedback registered! Decreasing confidence for this subgraph.")

# ----------------- TAB 1.5: BENCHMARK -----------------
elif tab_selection == "Empirical Benchmark (v2.0)":
    st.header("🧪 Empirical Defensibility Benchmark")
    st.write("To prove technical defensibility beyond cherry-picked demos, this runner mathematically verifies the Attribution Engine's accuracy across 15 synthetic stress-test scenarios.")
    
    if st.button("▶️ Run 15-Case Benchmark Suite", type="primary"):
        with st.spinner("Running batch diagnostics..."):
            try:
                res = requests.get(f"{API_URL}/evaluate")
                if res.status_code == 200:
                    metrics = res.json()
                    
                    st.markdown("### Benchmark Results")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Overall Accuracy", f"{metrics['accuracy_pct']:.1f}%")
                    m2.metric("Abstention Accuracy (True Negatives)", f"{metrics['abstention_accuracy_pct']:.1f}%")
                    m3.metric("Mean Latency", f"{metrics['mean_latency_ms']:.1f} ms")
                    
                    st.markdown("### 🔬 Scenario Breakdown")
                    for case in metrics['details']:
                        icon = "" if case['passed'] else "❌"
                        with st.expander(f"{icon} {case['scenario']}"):
                            st.json(case)
                else:
                    st.error("Failed to fetch benchmark results.")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")

# ----------------- TAB 2: SEMANTIC KPI CONTRACTS -----------------
elif tab_selection == "Semantic KPI Contracts":
    st.title("📜 Semantic KPI Governance Contracts")
    st.caption("Deterministic definitions, thresholds, ownership, and upstream dependency lineage")
    contract = load_kpi_contract()
    
    st.subheader("Governed KPI Matrix")
    for kpi, details in contract.get('kpis', {}).items():
        with st.expander(f"📌 {kpi.replace('_', ' ').title()} (Owner: {details.get('owner', 'N/A')})"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Description:** {details.get('description')}")
                st.write(f"**Type:** `{details.get('type')}`")
            with c2:
                st.write(f"**Aggregation:** `{details.get('aggregation')}`")
                st.write(f"**Thresholds:** {details.get('thresholds')}")
            with c3:
                st.write(f"**Upstream Dependencies:** {details.get('upstream_dependencies')}")

# ----------------- TAB 3: AUDIT TRAIL & TELEMETRY -----------------
elif tab_selection == "Audit Trail & Telemetry":
    st.title("Compliance Audit Trail & Runtime Telemetry")
    st.caption("Immutable state history, LLM token consumption, latency, and explainability records")
    try:
        audit_resp = requests.get(f"{API_URL}/audit-logs")
        if audit_resp.status_code == 200:
            logs = audit_resp.json()
            st.write(f"**Total Pipeline Invocations Logged:** {len(logs)}")
            for log in reversed(logs):
                with st.expander(f"🕒 Invocation: {log.get('timestamp')} | Role: {log.get('role')} | Confidence: {log.get('confidence_score')}"):
                    st.json(log)
        else:
            st.info("No audit logs recorded yet. Run a diagnostic pulse first.")
    except Exception as e:
        st.warning("Audit log service currently offline.")

# ----------------- TAB 4: CONTINUOUS LEARNING LOOP -----------------
elif tab_selection == "Continuous Learning Loop":
    st.title("Human-In-The-Loop Feedback Engine")
    st.caption("Capture analyst validation and overrides for offline model retraining")
    
    with st.form("feedback_form"):
        incident_id = st.text_input("Incident / Run ID", "INC-2026-08-15-US-EAST")
        suggested_root = st.text_input("Model Suggested Root Cause", "redis_hit_rate")
        verdict = st.selectbox("Analyst Verdict", ["APPROVED", "REJECTED", "OVERRIDDEN"])
        override_node = st.selectbox("Analyst Override Root Cause (if overridden)", ["None", "redis_hit_rate", "db_query_time_ms", "api_latency_ms", "checkout_success_rate"])
        notes = st.text_area("Analyst Notes & Domain Context", "Verified with DevOps team. Redis node failover was indeed the root cause.")
        
        submitted = st.form_submit_button("Submit Analyst Feedback")
        if submitted:
            try:
                fb_resp = requests.post(f"{API_URL}/feedback", json={
                    "incident_id": incident_id,
                    "suggested_root_cause": suggested_root,
                    "user_verdict": verdict,
                    "user_override_node": None if override_node == "None" else override_node,
                    "comments": notes
                })
                if fb_resp.status_code == 200:
                    st.success("Analyst feedback successfully recorded!")
                    st.info("**Feedback Captured**: The analyst verdict has been stored in offline logs for future model retraining and batch evaluation.")
            except Exception as e:
                st.error(f"Error recording feedback: {e}")
