# PAfE/PAX Intelligent Orchestrator: Enterprise Financial Systems Agentic Support

An asynchronous, multi-agent AI web service built using **CrewAI**, **FastAPI**, and **Python 3.11** to automate tier-1/tier-2 optimization, troubleshooting, and logic synthesis for **IBM Planning Analytics for Excel (PAfE / PAX)**. 

This platform serves as a critical bridge between rigid, multi-dimensional OLAP cubes (IBM TM1) and the fast-paced operational demands of **Regional CFOs, Controllers, Private Equity Analysts, and Real Estate Investment Managers** who rely on continuous, uninterrupted financial reporting.

---

## 💼 Business Context & Executive Value

In high-stakes environments—such as underwriting real estate portfolios, adjusting economic models for Private Equity, or closing quarterly books—Excel interface failures represent immediate operational risk. When a `PAX` task pane goes blank, an MDX view times out, or a cell-writeback fails, reporting bottlenecks trickle directly up to leadership.

This agentic system changes the support paradigm from **reactive IT ticket queues** to **instant, context-aware operational resolution**:

* **For Regional CFOs & Financial Controllers:** Eliminates reporting downtime during high-pressure close cycles. Ensures that regional rollup errors, multi-currency translations, and cube-writeback hitches are diagnosed in seconds, maintaining data integrity.
* **For Private Equity & Investment Management:** Protects active economic modeling workflows. Keeps underwriting models fluid by quickly rectifying broken data-retrieval formulas, active connection drops, or macro conflicts.
* **For Full-Service Real Estate Management:** Supports extensive property portfolio tracking and asset valuation reporting by parsing complex spreadsheet behaviors against underlying enterprise data warehouses.

---

## 🤖 Multi-Agent Architecture & Topology

The system orchestrates a specialized "Crew" of four autonomous micro-agents split rigidly by focus to prevent prompt distraction, enforce enterprise guardrails, and maximize execution speed:

```text
         [Incoming API JSON Payload / Data Discrepancy]
                               │
                               ▼
              ┌─────────────────────────────────┐
              │    1. PAX Telemetry Parser      │ ◄── Audits data lineage via regex/MDX tools,
              │         (gpt-4o-mini)           │     extracting formula patterns and faults.
              └────────────────┬────────────────┘
                               │
                               ▼ [Lineage Variance Context]
              ┌─────────────────────────────────┐
              │  2. CRE Underwriting Matcher    │ ◄── Runs Corrective RAG (CRAG) grading firewall
              │            (gpt-4o)             │     auditing materiality, syncing, & offsets.
              └────────────────┬────────────────┘
                               │
                               ▼ [Impact-Scoped Problem Definition]
              ┌─────────────────────────────────┐
              │    3. EPM Resolution Engine     │ ◄── Enforces Guardrails: Programmatically logs
              │         (gpt-4o-mini)           │     ServiceNow P1 tickets & alerts Cube Owner.
              └────────────────┬────────────────┘
                               │
                               ▼ [Escalated Tracking Confirmation]
              ┌─────────────────────────────────┐
              │  4. Executive Synthesis Bot     │ ◄── Packages ticket metrics and resolution
              │         (gpt-4o-mini)           │     status logs into markdown for CFOs.
              └─────────────────────────────────┘
```

### 🛡️ Enterprise Guardrail Matrix & Corrective RAG (CRAG) Firewall
The orchestration engine implements strict, deterministic functional limitations to protect multi-dimensional cube environments from data corruption or unauthorized automated adjustments. 

If the crew encounters an issue tied to **complex accounting treatments, cross-dimensional consolidation offsets (Project/Market/Joint Venture), or stranded in-memory "dirty cell" updates**, the system runs a specialized **CRAG Evaluation Gateway** tool to grade the telemetry context before executing any code.
1. **Deterministic Grading Check:** Evaluates numerical variances against a hardcoded **$50,000,000 Materiality Threshold** and checks for uncommitted dirty cells in the memory layer.
2. **Asynchronous Ticket Generation:** If a threshold breach or memory lock is flagged, the automation path freezes and dispatches a structured REST API payload to initialize an emergency ServiceNow P1 tracking ticket.
3. **Direct Cube Owner Alert:** Routes an automated warning via internal SMTP Relays containing raw lineage details, uncommitted record counts, and target impact models directly to the Human Expert.

---

## 🛠️ Repository Structure

This repository uses a decoupled, production-ready framework to ensure clean, cross-platform path mapping powered by `pathlib`:

```text
├── config/
│   ├── agents.yaml          # Declarative CrewAI roles, goals, and backstories
│   └── tasks.yaml           # Step-by-step execution pipelines and CRAG guardrails
├── src/
│   ├── __init__.py
│   ├── crew.py              # CrewAI initialization & lazy tool-import loading maps
│   ├── main.py              # FastAPI REST Web Gateway & Asynchronous background workers
│   └── tools/               # Custom Extension Module Toolkit
│       ├── crag_evaluator_tool.py # [NEW] Deterministic CRAG grading engine framework
│       ├── escalation_tool.py     # ServiceNow REST API and SMTP mail relay connector
│       ├── finance_diagnostics.py # [NEW] Financial data warehouse lineage auditor
│       ├── finreport_diagnostics.py # [NEW] Regex filters, MDX and risk mapping suite
│       └── mcp_mdx_tool.py        # MDX Query compiler with sliding rate limits & caching
├── .env.example             # Standardized template for environment variables
├── .gitignore               # Strict exclusion matrix (.venv, secrets, local caches)
└── requirements.txt         # Production-grade enterprise package dependencies
```

---

## 📋 Prerequisites

This tool is designed to be cross-platform and enterprise-ready. It has been fully verified across standard corporate hardware, including **Windows Enterprise environments**, **IBM laptops**, and **macOS (Intel and Apple Silicon M1-M4)**.

### 1. Runtime Environment
* **Python 3.11.x**: This project is built and optimized strictly for **Python 3.11**. Higher versions (like Python 3.12+) are not currently recommended due to specific framework and agent dependency constraints.
* **Package Manager**: `pip` (included with Python).

### 2. Enterprise & Network Requirements
* **IBM Planning Analytics Tools**: Ensure your environment has access to the required interfaces (**PAfE / PAX / PaCE** Excel add-ins) or direct connection strings to the TM1 REST API instance.
* **Network & VPN Access**: Active corporate network or VPN connectivity is required if your TM1 cubes or data tier reside behind an enterprise firewall.
* **API Authentication**: A valid environment configuration file (`.env`) populated with required enterprise or LLM pipeline API keys.

---

## 📦 Installation & Local Setup

### 1. Clone the Repository
Open your respective terminal and run:
```bash
git clone https://github.com
cd fpa-reporting-agent
```

### 2. Setup and Activate the Virtual Environment
To isolate project dependencies and prevent version conflicts with global Python packages, initialize a virtual environment based on your operating system:

#### 💻 On Windows Enterprise (PowerShell)
1. Generate the virtual environment folder:
   ```powershell
   python -m venv .venv
   ```
2. Enable script execution for your current session (required by many restricted enterprise profiles):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   ```
3. Activation:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

#### 🍏 On macOS Terminal (Zsh / Apple Silicon M1-M4)
1. Generate the virtual environment folder:
   ```bash
   /opt/homebrew/bin/python3.11 -m venv .venv
   ```
2. Activation:
   ```bash
   source .venv/bin/activate
   ```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a plain-text configuration file named `.env` in the root directory of the project and populate your tokens. **Do not track this file in Git.**

```env
# Enterprise LLM Pipeline Configuration
OPENAI_API_KEY=your_secure_api_key_here
OPENAI_MODEL_NAME_FAST=gpt-4o-mini
OPENAI_MODEL_NAME_ADVANCED=gpt-4o

# TM1 Server Target Environment Details
TM1_REST_API_URL=https://your-tm1-server-endpoint:8000
TM1_INSTANCE_NAME=CXMD
```

---

## 🚀 Execution & API Gateway Utilization

### 1. Launching the Microservice
Start the FastAPI server locally inside your activated environment by executing:
```bash
python src/main.py
```
The server will bind to `http://127.0.0.1:8000`. You can interact with the auto-generated documentation portal at **`http://127.0.0`**.

### 2. Triggering an Audit Payload (`POST /api/v1/diagnose`)
