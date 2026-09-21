import os
import sys
import logging
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field
import uvicorn

# Inject absolute path references into system engine to resolve runtime module lookups seamlessly
sys.path.append(str(Path(__file__).resolve().parent))

# Establish rigorous corporate logging topology
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("EPM_Orchestrator_API")

# Initialize the Core FastAPI Engine
app = FastAPI(
    title="PAfE/PAX Intelligent Orchestrator API",
    description="Enterprise REST gateway for multi-agent OLAP cube diagnostics and automated human escalation.",
    version="1.0.0"
)

# Global dictionary to track long-running pipeline execution jobs
JOB_REGISTRY: Dict[str, Dict[str, Any]] = {}

# --- PHASE 1: ENTERPRISE DATA INGESTION SCHEMAS ---
class DiagnosticRequest(BaseModel):
    business_unit: str = Field(..., example="BU_7400_CRE_PE", description="Target Business Unit string identifier.")
    target_intersection: str = Field(..., example="Project:JV_09_Offset, Market:NY_Metro", description="Multi-dimensional coordinate string.")
    measure: str = Field(..., example="Net_Asset_Value", description="Target accounting metric cell.")
    user_reported_anomaly: str = Field(..., example="Spreadsheet variance of $64.2M", description="Raw text context from user.")

class PipelineResponse(BaseModel):
    job_id: str
    status: str
    timestamp: str
    message: str


# --- PHASE 2: ASYNCHRONOUS PIPELINE BRIDGE ---
class OrchestrationWorker:
    def __init__(self):
        from crew import PafeIntelligentOrchestrator
        self.orchestrator = PafeIntelligentOrchestrator()
        self.crew_instance = self.orchestrator.crew()

    def run_sync_kickoff(self, inputs: dict) -> str:
        """Executes the CrewAI orchestration loop synchronously."""
        return self.crew_instance.kickoff(inputs=inputs)


# --- PHASE 3: ENDPOINT ROUTING MATRIX ---

@app.get("/health", status_code=status.HTTP_200_OK, summary="System Vital Check")
def check_api_health():
    """Returns the operational baseline state of the API gateway."""
    return {
        "status": "ONLINE",
        "timestamp": datetime.utcnow().isoformat(),
        "environment_configured": os.getenv("OPENAI_API_KEY") is not None
    }


@app.post("/api/v1/diagnose", response_model=PipelineResponse, status_code=status.HTTP_202_ACCEPTED, summary="Trigger Agentic Audit")
def trigger_agentic_diagnostic(payload: DiagnosticRequest, background_tasks: BackgroundTasks):
    """
    Ingests a financial variance telemetry report and assigns it to the multi-agent crew.
    Dispatches immediately as a non-blocking background worker to prevent HTTP gateway timeouts.
    """
    job_id = f"JOB-{int(datetime.utcnow().timestamp())}"
    
    inputs = {
        "business_unit": payload.business_unit,
        "target_intersection": payload.target_intersection,
        "measure": payload.measure,
        "user_reported_anomaly": payload.user_reported_anomaly
    }

    JOB_REGISTRY[job_id] = {
        "status": "PROCESSING",
        "started_at": datetime.utcnow().isoformat(),
        "inputs": inputs,
        "result": None
    }

    # Assign processing onto an isolated background worker thread
    background_tasks.add_task(async_pipeline_executor, job_id, inputs)

    return PipelineResponse(
        job_id=job_id,
        status="ACCEPTED",
        timestamp=datetime.utcnow().isoformat(),
        message="Telemetry successfully queued. Agents are actively constructing data lineage audit paths."
    )


@app.get("/api/v1/jobs/{job_id}", summary="Fetch Audit Results")
def get_diagnostic_job_status(job_id: str):
    """Securely retrieve final executive summaries, cache metrics, or active ServiceNow tracking incident codes."""
    if job_id not in JOB_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The tracking key '{job_id}' does not exist inside active registry archives."
        )
    return JOB_REGISTRY[job_id]


# --- PHASE 4: ASYNCHRONOUS BACKGROUND WORKER ---
def async_pipeline_executor(job_id: str, inputs: dict):
    """Executes multi-agent loops without locking or blocking the main network server thread."""
    logger.info(f"⚙️ Background thread pool captured tracking block: {job_id}")
    try:
        worker = OrchestrationWorker()
        raw_markdown_output = worker.run_sync_kickoff(inputs)
        
        JOB_REGISTRY[job_id]["status"] = "COMPLETED"
        JOB_REGISTRY[job_id]["completed_at"] = datetime.utcnow().isoformat()
        JOB_REGISTRY[job_id]["result"] = raw_markdown_output
        logger.info(f"✅ Background job task successfully closed out: {job_id}")
        
    except Exception as background_err:
        logger.error(f"🚨 Background processing failure on task {job_id}: {str(background_err)}")
        JOB_REGISTRY[job_id]["status"] = "FAILED"
        JOB_REGISTRY[job_id]["error"] = str(background_err)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
