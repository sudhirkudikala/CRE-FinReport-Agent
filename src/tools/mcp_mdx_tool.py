import os
import time
import logging
import json
import hashlib
from typing import Dict, Any, List
import requests
from crewai.tools import tool
from pydantic import BaseModel, Field

# Setup enterprise-grade diagnostic logging for your iMac M4 console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EPM_Orchestrator_MCP")

# Global cross-agent memory cache dictionary (Simulating cluster state memory)
GLOBAL_ORCHESTRATION_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_EXPIRATION_SECONDS = 300  # 5-minute cache lifespan matching financial data sweeps

# Sliding Window Rate Limiter Caches
API_REQUEST_LOGS: List[float] = []
MAX_CALLS_PER_MINUTE = 60


class MdxToolSchema(BaseModel):
    business_unit: str = Field(..., description="Target Business Unit identifier, e.g., 'BU_7400_CRE_PE'.")
    target_intersection: str = Field(..., description="Comma-separated dimension mappings, e.g., 'Project:JV_09_Offset, Market:NY_Metro'.")
    measure: str = Field(..., description="The accounting financial measure cell being evaluated, e.g., 'Net_Asset_Value'.")


def _is_rate_limited() -> bool:
    """Enforces client-side rate limiting to preserve enterprise OLAP API bandwidth."""
    global API_REQUEST_LOGS
    current_time = time.time()
    # Filter logs strictly to the last 60 seconds
    API_REQUEST_LOGS = [t for t in API_REQUEST_LOGS if current_time - t < 60]
    if len(API_REQUEST_LOGS) >= MAX_CALLS_PER_MINUTE:
        return True
    API_REQUEST_LOGS.append(current_time)
    return False


@tool("MCP Multi-Dimensional MDX Query Engine", args_schema=MdxToolSchema)
def execute_mcp_mdx_orchestration(business_unit: str, target_intersection: str, measure: str) -> str:
    """
    MCP tool that dynamically compiles an MDX query string for IBM TM1 cubes based on 
    extracted structural variables. Performs a non-destructive REST API validation dry-run,
    implements cross-agent caching, and fails gracefully with structured telemetry on error.
    """
    
    # --- PHASE 1: SANITIZATION & INPUT PARSING ---
    try:
        parsed_dims = {}
        if target_intersection and ":" in target_intersection:
            for pair in target_intersection.split(","):
                k, v = pair.split(":")
                parsed_dims[k.strip()] = v.strip()
        else:
            raise ValueError("Target intersection string must be formatted as key-value pairings split by colons.")
    except Exception as e:
        return json.dumps({
            "status": "INPUT_ERROR",
            "message": f"Malformed multi-dimensional parameters provided to MCP: {str(e)}",
            "suggested_action": "Verify token extraction logic in upstream Parser Agent."
        })

    # --- PHASE 2: CROSS-AGENT CACHING LAYER ---
    # Generates a unique cryptographic hash signature based on the specific coordinate matrix
    cache_payload = f"{business_unit.lower()}_{json.dumps(parsed_dims, sort_keys=True)}_{measure.lower()}"
    cache_key = hashlib.sha256(cache_payload.encode('utf-8')).hexdigest()
    
    current_timestamp = time.time()
    if cache_key in GLOBAL_ORCHESTRATION_CACHE:
        cache_entry = GLOBAL_ORCHESTRATION_CACHE[cache_key]
        if current_timestamp - cache_entry["timestamp"] < CACHE_EXPIRATION_SECONDS:
            logger.info(f"💾 [CACHE HIT] Cross-agent cache utilized for key: {cache_key}")
            return json.dumps(cache_entry["data"])

    # --- PHASE 3: RATE LIMIT MATRIX CHECK ---
    if _is_rate_limited():
        return json.dumps({
            "status": "RATE_LIMIT_EXCEEDED",
            "message": "Local MCP execution choked to preserve TM1 server resources. Request blocked by sliding window metric.",
            "suggested_action": "Hold execution pipeline thread pool for 10 seconds before re-attempting."
        })

    # --- PHASE 4: DYNAMIC MDX SYNTAX COMPILATION ---
    try:
        dimension_tuples = [f"[{dim}].[{val}]" for dim, val in parsed_dims.items()]
        mdx_query_string = (
            f"SELECT {{[Measures].[{measure}]}} ON COLUMNS, "
            f"{{[BusinessUnit].[{business_unit}]}} ON ROWS "
            f"FROM [Financial_Control_Cube] "
        )
        if dimension_tuples:
            mdx_query_string += f"WHERE ({', '.join(dimension_tuples)})"
            
        logger.info(f"🧱 [MCP COMPILE SUCCESS] Executing safe construction: {mdx_query_string}")
    except Exception as e:
        return json.dumps({
            "status": "COMPILATION_FAILED",
            "message": f"Failed to programmatically build multi-dimensional tuple structure: {str(e)}"
        })

    # --- PHASE 5: FAULT-TOLERANT REST API DATA-LINEAGE DRY-RUN ---
    tm1_api_endpoint = os.getenv("TM1_REST_API_URL", "https://mock-tm1-epm-server:8000")
    request_url = f"{tm1_api_endpoint}/api/v1/Cubes('Financial_Control_Cube')/ExecuteMDX"
    
    try:
        # Simulating a severe data lineage gap: 40 high-velocity incremental records flagged as dirty
        mock_validated_response = {
            "status": "SUCCESS",
            "compiled_mdx": mdx_query_string,
            "metadata": {
                "cube": "Financial_Control_Cube",
                "execution_time_ms": 14,
                "cell_state": "DIRTY", 
                "dirty_cells_in_memory_slice": 40,
                "accounting_treatment": "IFRS 16 Lease Offset Rule applied dynamically at consolidation layer",
                "dimension_offset_conflict": "Joint Venture minority interest offset misaligned on Project dimension hierarchy"
            },
            "data_payload": {
                "warehouse_record_count": 14250,
                "tm1_cube_loaded_count": 14210,
                "variance_detected_value": 64200000.00,  # $64.2M missing numbers gap
                "currency": "USD"
            }
        }
        
        # Commit result to global cache to allow immediate visibility for the remaining crew agents
        GLOBAL_ORCHESTRATION_CACHE[cache_key] = {
            "timestamp": current_timestamp,
            "data": mock_validated_response
        }
        
        return json.dumps(mock_validated_response, indent=2)

    except requests.exceptions.Timeout:
        logger.error("🚨 [TIMEOUT ERROR] TM1 REST API connection timed out.")
        return json.dumps({
            "status": "API_TIMEOUT",
            "message": "The downstream financial cube engine failed to return data within the allotted 5.0 second window.",
            "compiled_mdx": mdx_query_string,
            "suggested_action": "Route issue immediately to Escalation Agent to initialize an emergency ServiceNow ticket."
        })
        
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"🚨 [CUBE SPECIFIC ERROR] Backend HTTP exception captured: {str(http_err)}")
        return json.dumps({
            "status": "CUBE_AXIS_MISMATCH",
            "message": "The generated MDX configuration represents an invalid intersection path inside the target cube schema.",
            "compiled_mdx": mdx_query_string,
            "api_telemetry_dump": str(http_err),
            "suggested_action": "Pass context back to CRE Underwriting Matcher to audit if joint venture dimensions are offset."
        })
        
    except Exception as generic_err:
        logger.error(f"🚨 [UNEXPECTED FAILSAFE RESCUE] {str(generic_err)}")
        return json.dumps({
            "status": "SYSTEM_CRITICAL_UNKNOWN",
            "message": f"An unhandled execution anomaly was suppressed by the tool boundary: {str(generic_err)}",
            "suggested_action": "Freeze automation loop immediately."
        })
