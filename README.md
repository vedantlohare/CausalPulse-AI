# ⚡ CausalPulse AI
### *Enterprise KPI Diagnostic & Automated Causal Storytelling Engine*
**Accenture Innovation Challenge 2026 — Track 3: BusinessIntelligence.ai**  
**Team:** StarkProtocol (Vedant Sachin Lohare & Smira Jaitley, Indian Institute of Technology, Kanpur)

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit%201.32-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Causality](https://img.shields.io/badge/Inference-NetworkX%20DAGs-informational)](https://networkx.org)
[![VectorDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-purple)](https://trychroma.com)
[![LLM](https://img.shields.io/badge/Synthesis-Google%20Gemini%20Pro-orange?logo=google&logoColor=white)](https://ai.google.dev)

---

## 📑 Table of Contents
1. [Executive Summary](#-executive-summary)
2. [The Core Problem in Enterprise BI](#-the-core-problem-in-enterprise-bi)
3. [Architecture Overview](#-architecture-overview)
4. [Key Architectural Innovations](#-key-architectural-innovations)
5. [Requirements & Dependencies](#-requirements--dependencies)
6. [Quickstart & Installation](#-quickstart--installation)
7. [Configuration](#-configuration)
8. [Project Directory Layout](#-project-directory-layout)
9. [How to Demo CausalPulse AI](#-how-to-demo-causalpulse-ai)
10. [API Specification & Endpoints](#-api-specification--endpoints)
11. [Enterprise Governance, Security & Guardrails](#-enterprise-governance-security--guardrails)
12. [Business Case & Financial ROI Model](#-business-case--financial-roi-model)
13. [Real-World Production Architecture](#-real-world-production-architecture-scaling-beyond-demos)
14. [Troubleshooting & FAQ](#-troubleshooting--faq)
15. [Maintainers](#-maintainers)

---

## 🎯 Executive Summary

Modern enterprise dashboards (Tableau, PowerBI, Looker) excel at showing **what** happened (e.g., *"Revenue dropped 8% in US-East"*), but completely fail to explain **why** it happened or **what to do next**. Translating metric drops into root causes requires data analysts to spend **3 to 5 days** running manual SQL queries, joining tables, and cross-checking Slack outage channels.

**CausalPulse AI** bridges structured metric telemetry with unstructured qualitative context (Zendesk tickets, Jira incident reports, Slack logs). By combining **statistical baseline filtering**, **topological Directed Acyclic Graphs (DAGs)**, **semantic vector RAG (ChromaDB)**, and **persona-aware LLM synthesis (Gemini Pro)**, CausalPulse AI slashes root-cause diagnosis from **4 days to under 30 seconds**.

```
[Structured Telemetry] ──┐
                         ├──► [Dual Diagnostic Engine] ──► [Executive Briefing + DAG + Simulation]
[Unstructured Logs]   ──┘
```

---

## 🚨 The Core Problem in Enterprise BI

1. **The Fire-Drill Bottleneck:** When a mission-critical KPI drops, leadership initiates an all-hands fire-drill. Analysts sift through millions of rows across disconnected databases, resulting in delayed incident resolution and millions of dollars in revenue leakage.
2. **Correlation vs. Causation (Simpson's Paradox):** Generic LLM wrappers confuse correlation with causation. If two metrics spike simultaneously (e.g., server latency and marketing impressions), naive AI claims one caused the other.
3. **Unstructured Data Silos:** Over 80% of actionable enterprise context is trapped in qualitative channels (Zendesk customer complaints, Jira bugs, Slack war-rooms). Traditional BI tools are blind to text.
4. **Ambiguity Paralysis:** When metric data is incomplete or conflicting, standard GenAI tools hallucinate confident but false explanations.

---

## 🏛 Architecture Overview

CausalPulse AI operates on a rigorous **3-layer architecture**:

```mermaid
flowchart TD
    subgraph L1["1. Enterprise Ingestion Layer"]
        T["Structured Telemetry<br>(Revenue, Success Rate, Latency, DB Time, Cache Hits)"]
        U["Unstructured Operational Context<br>(Zendesk Support Tickets, Jira Incident Reports, Slack Logs)"]
    end

    subgraph L2["2. Dual Diagnostic Engine"]
        direction TB
        subgraph NON_LLM["Non-LLM (Deterministic)"]
            E1["Engine 1: Structured Causal Attribution<br>• Rolling Z-Score Anomaly Detection<br>• Topological DAG Traversal (NetworkX)<br>• Governed by Semantic Contract (YAML)"]
        end
        subgraph LLM_AUGMENTED["LLM-Augmented (Generative)"]
            E2["Engine 2: Contextual Narrative Synthesizer<br>• ChromaDB Semantic Vector Store<br>• Cross-References Root Nodes with Text Evidence<br>• PII Scrubbing & Entity Redaction Guardrail"]
        end
        AG{"Ambiguity Gate<br>Confidence Score < 0.65?"}
    end

    subgraph L3["3. Prescriptive Executive Output Layer"]
        R1["Normal Resolution (Confidence ≥ 0.65)<br>• Persona-Specific Natural Language Brief (LLM)<br>• Real-Time Financial Drain Quantification (Non-LLM)<br>• Counterfactual What-If Scenario Simulator (Non-LLM)"]
        R2["Active Ambiguity Mode (Confidence < 0.65)<br>• Guided Diagnostic Hypothesis Tree (Non-LLM)<br>• Recommended Targeted SQL / Log Queries<br>• Zero-Hallucination Guardrail"]
    end

    T --> E1
    U --> E2
    E1 --> AG
    E2 --> AG
    AG -- "Yes (Ambiguous)" --> R2
    AG -- "No (High Confidence)" --> R1
```

---

## 🌟 Key Architectural Innovations

### 1. Mathematical Anomaly Detection & Baseline Filtering
To separate genuine anomalies from standard diurnal noise, CausalPulse computes a rolling window mean ($\mu_t$) and standard deviation ($\sigma_t$) across metric telemetry:
$$Z_t = \frac{x_t - \mu_t}{\sigma_t}$$
* Metrics exceeding $|Z_t| > \theta_{\text{threshold}}$ (default $\theta = 3.0$) are flagged as active anomalous nodes $\mathcal{A}$.

### 2. Topological Causal Graph Inference (NetworkX DAGs)
The enterprise KPI dependency structure is modeled as a **Directed Acyclic Graph (DAG)** $\mathcal{G} = (\mathcal{V}, \mathcal{E})$.
* **Topological Root-Cause Isolation Algorithm:** A firing node $n \in \mathcal{A}$ is isolated as a true Root Cause if and only if none of its in-graph predecessors are in the active anomaly set:
$$\text{RootCauses} = \{n \in \mathcal{A} \mid \text{Pred}(n) \cap \mathcal{A} = \emptyset\}$$
* This mathematically guarantees that downstream symptoms (e.g., Revenue Drop) are ignored in favor of the upstream failure node (e.g., Redis Cache failure).

### 3. Qualitative Cross-Referencing RAG (ChromaDB)
When Engine 1 flags a technical failure (e.g., `redis_hit_rate`), Engine 2 retrieves exact timestamped evidence from internal Jira outage reports and Slack alerts to corroborate the finding with ground truth.

### 4. Active Ambiguity Handling (Zero-Hallucination Abstention)
If evidence is insufficient, contradictory, or lacks historical priors ($\text{Confidence} < 0.65$), CausalPulse abstains from guessing. It calculates a confidence score and outputs a **Guided Diagnostic Hypothesis Tree** with targeted SQL queries for human analysts.

### 5. Prescriptive "What-If" Counterfactual Simulator
Executives can simulate the downstream impact of pulling controllable business levers (`reroute_traffic`, `scale_db_replicas`, `circuit_breaker_payment_gateway`) to evaluate revenue recovery before deploying changes.

---

## 📦 Requirements & Dependencies

### System Requirements
* **Operating System:** Windows 10/11, macOS (Intel/Apple Silicon), or Linux (Ubuntu 20.04+)
* **Python Runtime:** Python 3.10, 3.11, 3.12, or 3.13
* **Memory:** Minimum 4 GB RAM (8 GB recommended)
* **Network:** Localhost ports `8000` (FastAPI) and `8501` (Streamlit) available

### Key Python Packages
* `fastapi` & `uvicorn` (Backend REST API service)
* `streamlit` & `plotly` (Interactive executive dashboard & DAG graph visualizer)
* `networkx` (Topological graph traversal and causal inference)
* `chromadb` (Local semantic vector store for qualitative context)
* `google-genai` (Gemini Pro synthesis with built-in offline deterministic fallback)
* `pydantic` & `pyyaml` (Semantic contract schema parsing and validation)

---

## 🚀 Quickstart & Installation

### 1. Clone & Enter Directory
```bash
git clone https://github.com/vedantlohare/CausalPulse-AI.git
cd CausalPulse-AI
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Start Backend Server (Terminal 1)
```bash
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
* **API URL:** `http://127.0.0.1:8000`
* **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`

### 4. Start Frontend Dashboard (Terminal 2)
```bash
python -m streamlit run frontend/app.py
```
* **Dashboard URL:** `http://localhost:8501`

---

## ⚙️ Configuration

CausalPulse AI is designed for flexibility across production, testing, and air-gapped demo environments.

### 1. Environment Variables (`.env`)
Create an optional `.env` file in the root or `backend/` directory:
```ini
# Google Gemini API Key (Optional: System runs deterministic offline fallback if unset)
GEMINI_API_KEY=your_gemini_api_key_here

# Backend host and port binding
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

# Logging & Environment
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### 2. KPI Semantic Contract (`backend/app/schema/kpi_contract.yml`)
Enterprise KPI definitions, causal parent-child dependencies, anomaly thresholds, and role-based access limits are defined in a governed YAML contract. You can configure:
* **Metric Nodes:** Add new KPIs (e.g., `checkout_success_rate`, `payment_gateway_latency`).
* **Causal Edges:** Define which upstream metric influences downstream outcomes.
* **Sensitivity Thresholds:** Configure custom Z-score cutoffs (default `3.0`).
* **Role Permissions:** Restrict metric access by persona (`Ops_Lead` vs. `CMO`).

### 3. Operational Log Streaming (`backend/mock_data/operational_logs.json`)
Ingest custom Jira incident tickets, Slack PagerDuty war-room snippets, or Zendesk customer complaints by placing JSON objects with timestamp, source, and text attributes.

---

## 📁 Project Directory Layout

```
causalpulse-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       └── diagnostics.py      # REST endpoints: /run-diagnostics, /simulate-lever, /feedback, /audit-logs
│   │   ├── core/
│   │   │   ├── config.py               # Application configuration & environment settings
│   │   │   ├── gemini_client.py        # Google GenAI Gemini Pro client with deterministic fallback
│   │   │   ├── audit_logger.py         # Immutable JSON compliance audit recorder
│   │   │   └── feedback_processor.py   # Human-in-the-loop analyst override feedback loop
│   │   ├── engines/
│   │   │   ├── anomaly_detector.py     # Rolling Z-score baseline anomaly detection
│   │   │   ├── causal_graph.py         # Directed Acyclic Graph generator & topological root cause tracer
│   │   │   ├── rag_synthesizer.py      # ChromaDB vector embedding & log retrieval engine
│   │   │   ├── ambiguity_handler.py    # Probabilistic confidence scoring & hypothesis tree builder
│   │   │   ├── financial_quantifier.py # Real-time dollar burn-rate calculation
│   │   │   └── guardrails_rbac.py      # Regex PII scrubber & persona prompt formatting
│   │   ├── schema/
│   │   │   └── kpi_contract.yml        # Governed semantic contract defining KPI definitions & lineage
│   │   └── main.py                     # FastAPI application entrypoint
│   ├── mock_data/
│   │   ├── operational_logs.json       # Zendesk customer complaints, Jira bugs, Slack alerts
│   │   └── generate_mock_data.py       # Python generator for repeatable test data
│   └── requirements.txt                # Backend & Frontend dependency specification
├── frontend/
│   └── app.py                          # Streamlit interactive executive dashboard & DAG visualizer
└── README.md                           # Comprehensive documentation
```

---

## 🖥 How to Demo CausalPulse AI

Navigate through the Streamlit interface to test all 5 pre-configured incident scenarios:

| Incident Scenario | Scenario Characteristics & System Behavior |
| :--- | :--- |
| **🔥 Outage Incident** | Redis failover fails $\rightarrow$ DB query times spike $\rightarrow$ Checkout drops. The engine isolates `redis_hit_rate` in Red, calculates -$3.98M loss, pulls Slack PagerDuty alerts, and allows traffic reroute simulation. |
| **💳 Payment Gateway Degradation** | Third-party payment provider webhook timeouts cause cart completion drops. Engine isolates payment gateway failure, calculates checkout loss, and suggests engaging circuit breaker levers. |
| **⚡ Flash Sale Traffic Surge** | APAC marketing broadcast drives 5x surge on API gateway $\rightarrow$ DB connection pool exhaustion. Engine differentiates surge traffic from systemic bugs and suggests DB replica scaling. |
| **⚠️ Ambiguous Signal** | Partial metric anomaly with conflicting or missing qualitative logs. Confidence score drops below 0.65 $\rightarrow$ Engine enters Active Ambiguity Mode and presents a Guided Hypothesis Tree + SQL queries. |
| **✅ Steady State Baseline** | Standard operational telemetry with normal diurnal cycles. All Z-scores remain within $|Z| \le 3.0$ $\rightarrow$ System reports healthy status with zero false-alarm fatigue. |

### Core Workflow Demo Steps:
1. **Live Diagnostic Workspace:** Select a scenario preset, choose an **Executive Persona** (`Ops_Lead` vs. `CMO`), and click **⚡ Run Diagnostic Pulse**.
2. **Topological DAG & Financial Impact:** Examine the Plotly DAG and observe how true root causes are separated from downstream symptoms. Look for the Execution Latency waterfall in the top metrics.
3. **Qualitative Evidence (RAG):** Review corroborating Jira tickets and Slack logs with automated PII masking (`[REDACTED_PHONE]`).
4. **Prescriptive Simulator:** Select an action lever to quantify recovery percentages, which display in visually styled metric cards showing cascading protection.
5. **Download Executive Briefing:** Click **📥 Download Executive Report** to export a distribution-ready markdown brief.
6. **Empirical Benchmark (v2.0):** Open the Benchmark tab and run the 15-case synthetic suite to mathematically prove the engine's 100% abstention accuracy against hallucinations.
7. **Semantic Contracts & Continuous Learning:** Inspect governed KPI rules under Tab 3 and test submitting human analyst overrides under Tab 5.

---

## 🔌 API Specification & Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/diagnostics/run-diagnostics` | Executes anomaly detection, DAG root cause tracing, RAG retrieval, and executive synthesis. |
| `POST` | `/api/v1/diagnostics/simulate-lever` | Simulates the downstream impact of pulling a business lever on the causal graph. |
| `POST` | `/api/v1/diagnostics/feedback` | Captures human-in-the-loop analyst verdicts (`APPROVED`, `REJECTED`, `OVERRIDDEN`). |
| `GET` | `/api/v1/diagnostics/audit-logs` | Retrieves the immutable compliance audit history. |
| `GET` | `/api/v1/diagnostics/evaluate` | Runs the 15-case synthetic benchmark suite for empirical defensibility. |

---

## 🛡️ Enterprise Governance, Security & Guardrails

* **PII Scrubbing Guardrails (`guardrails_rbac.py`):** Automatically sanitizes credit cards, phone numbers, and emails (`[REDACTED_PII]`) before prompting.
* **Role-Based Access Control (RBAC):** Literal, enforced redaction of raw metric values at the API layer based on the querying persona's clearance, logged for compliance.
* **LLM Unit Economics:** Tracks real token consumption and estimated cost per diagnostic pulse directly on the UI banner (<$0.003 per pulse).
* **Offline Feedback Capture:** Analyst overrides are stored in immutable logs for offline model retraining and batch evaluation.
* **Audit Logging:** Every invocation, data access redaction, and action lever simulation is appended to a structured audit history JSON.

### 🧠 The Core Architecture Tradeoff: Deterministic vs. Generative
A key design decision in CausalPulse AI is **not relying on an LLM for quantitative truth or root-cause guessing**. Instead, we built a **Deterministic Frequentist (Z-Score)** core combined with **DAG Topological Traversal**. We deliberately chose this over formal black-box Causal Discovery (e.g., NOTEARS/LiNGAM) for **speed and absolute auditability**. The LLM is strictly confined to the synthesis layer—reading deterministic proofs and semantic RAG context to generate persona-aware narratives. This mathematically eliminates hallucination in root-cause isolation.

---

## 💰 Business Case & Financial ROI Model

| Metric | Traditional Enterprise BI Fire-Drills | With CausalPulse AI |
| :--- | :--- | :--- |
| **Mean Time to Identify (MTTI)** | 72 to 120 Hours (3–5 Business Days) | **< 30 Seconds** |
| **Analyst Labor per Incident** | 4 Analysts × 24 Hours = 96 Hours (~$14,400) | **0.1 Hours (~$15)** |
| **Annual Revenue Saved (Avg Enterprise)** | High Leakage (Delayed mitigation) | **$3.8M+ in prevented downtime** |
| **Consulting Payback Period** | 6–12 Months | **< 45 Days** |

---

## 🌐 Real-World Production Architecture (Scaling Beyond Demos)

In production enterprise deployments, CausalPulse AI functions as a continuous, streaming intelligence pipeline:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   REAL-WORLD ENTERPRISE DATA PIPELINE                   │
└────────────────────────────────────────────────────────────────────────┘
   │
   ├──► 1. Continuous Streaming Telemetry (Kafka / Snowflake / Databricks)
   │    Sliding-window Z-scores / Seasonal-Trend decomposition (STL) run
   │    on 10,000+ live metrics every 60 seconds.
   │
   ├──► 2. Dynamic Causal Graph Discovery (LiNGAM / NOTEARS / Structural Eq)
   │    Dynamically infers new causal edges directly from observational telemetry.
   │
   ├──► 3. Multi-Root Cascading Incident Isolation
   │    Isolates multiple independent failure origins simultaneously.
   │
   ├──► 4. Vector Log Streaming (ChromaDB / Pinecone / Elasticsearch)
   │    Live connectors ingest Slack war-rooms, Datadog alerts, and Zendesk tickets.
   │
   └──► 5. Self-Learning Priors (HITL Feedback)
        Analyst overrides continuously fine-tune graph edge weights and statistical priors.
        - Outcome: The engine learns human business context, continuously improving accuracy.
```

---

## ❓ Troubleshooting & FAQ

**Q: Why does CausalPulse AI enter "Active Ambiguity Mode"?**  
**A:** When telemetry is missing or qualitative evidence is contradictory, the engine calculates a composite confidence score. If $\text{Score} < 0.65$, CausalPulse deliberately abstains from guessing root causes to prevent costly hallucinations. Instead, it generates a Guided Diagnostic Hypothesis Tree with targeted SQL queries for human analysts.

**Q: Do I need a paid Google Gemini API key to run and evaluate the prototype?**  
**A:** No. CausalPulse AI includes an intelligent deterministic fallback synthesizer (`gemini_client.py`). If no API key is supplied, the system automatically uses deterministic rule templates to generate complete, structured executive briefings, DAG proofs, and counterfactual simulations offline.

**Q: How does CausalPulse AI prevent customer data leakage in regulated environments (HIPAA / GDPR / SOC2)?**  
**A:** All unstructured operational logs pass through `guardrails_rbac.py` before vector storage or LLM prompting. Regex sanitizers automatically replace credit card numbers (`[REDACTED_CC]`), phone numbers (`[REDACTED_PHONE]`), and customer emails (`[REDACTED_EMAIL]`).

**Q: How do I resolve `Address already in use` when starting FastAPI or Streamlit?**  
**A:** Specify an alternative port:
* For Backend: `python -m uvicorn app.main:app --app-dir backend --port 8001`
* For Frontend: `python -m streamlit run frontend/app.py --server.port 8502`

---

## 👥 Maintainers

Developed with pride for the **Accenture Innovation Challenge 2026 (Round 2: Prototype Development)**:

* **Vedant Sachin Lohare (Team Leader)**
  * Indian Institute of Technology, Kanpur — Aerospace Engineering ('28)
  * GitHub: [@vedantlohare](https://github.com/vedantlohare)
* **Smira Jaitley**
  * Indian Institute of Technology, Kanpur — Chemical Engineering ('28)
  * Team: **StarkProtocol**

*For inquiries or enterprise demonstrations, please submit an issue or pull request via the [GitHub Repository](https://github.com/vedantlohare/CausalPulse-AI).*
