#!/usr/bin/env bash

# ====================================================================================
# PAfE/PAX Intelligent Orchestrator: Local Integration Validation Script
# Automated background worker polling and end-to-end FastAPI endpoint fuzzing.
# ====================================================================================

# Terminal Visual Anchors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0;0m' # No Color

API_BASE="http://127.0.0.1:8000"

echo -e "${CYAN}[1/4] Initializing Local Runtime Safety Checks...${NC}"

# Ensure Python virtual environment is active
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [ -f ".venv/bin/activate" ]; then
        echo -e "${YELLOW}-> Auto-activating local .venv partition...${NC}"
        source .venv/bin/activate
    else
        echo -e "${RED}🚨 Error: Local .venv directory not detected. Run installation steps first.${NC}"
        exit 1
    fi
fi

# Verify FastAPI application is responding on the local gateway network slice
echo -e "${CYAN}[2/4] Verifying Target Gateway Connectivity...${NC}"
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/health")

if [ "$HEALTH_CHECK" != "200" ]; then
    echo -e "${YELLOW}⚠️ FastAPI server is offline. Spawning background instance via uvicorn...${NC}"
    
    # FORCE EXECUTION THROUGH YOUR LOCKED VIRTUAL ENVIRONMENT PYTHON PARTITION
    ./.venv/bin/python src/main.py > server_error.log 2>&1 &
    SERVER_PID=$!
    
    # Allow local kernel sockets 4 seconds to complete internal initialization
    sleep 4

    
    # Allow local kernel sockets 3 seconds to complete internal initialization
    sleep 3
    
    # Re-verify health checkpoint
    HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/health")
    if [ "$HEALTH_CHECK" != "200" ]; then
        echo -e "${RED}🚨 Error: Failed to initialize local FastAPI endpoint on port 8000.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Local server successfully bound to PID: $SERVER_PID${NC}"
fi

# --- PHASE 3: TELEMETRY INGESTION PAYLOAD ---
echo -e "${CYAN}[3/4] Submitting Non-Blocking High-Materiality Test Payload to /api/v1/diagnose...${NC}"

# Fire structured multi-dimensional discrepancy array up to the gateway
RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/diagnose" \
  -H 'Content-Type: application/json' \
  -d '{
    "business_unit": "BU_7400_CRE_PE",
    "target_intersection": "Project:JV_09_Offset, Market:NY_Metro",
    "measure": "Net_Asset_Value",
    "user_reported_anomaly": "Balance sheet short by $64.2M. PAX view completely frozen with uncommitted dirty cell logs."
  }')

# Extract unique job key identifier token using clean bash regex manipulation
JOB_ID=$(echo "$RESPONSE" | grep -o '"job_id":"[^"]*' | grep -o '[^"]*$')

if [ -z "$JOB_ID" ]; then
    echo -e "${RED}🚨 Error: Ingestion rejected. Server response summary: $RESPONSE${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Telemetry Accepted! Tracking Key Generated: ${YELLOW}$JOB_ID${NC}"

# --- PHASE 4: BACKGROUND WORKER POLLING REGISTRY LOOP ---
echo -e "${CYAN}[4/4] Activating Local Registry Polling Infrastructure...${NC}"
MAX_RETRIES=15
RETRY_COUNT=0
DELAY_SECONDS=4

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    JOB_STATUS_PAYLOAD=$(curl -s "$API_BASE/api/v1/jobs/$JOB_ID")
    STATUS_TOKEN=$(echo "$JOB_STATUS_PAYLOAD" | grep -o '"status":"[^"]*' | grep -o '[^"]*$')
    
    if [ "$STATUS_TOKEN" == "COMPLETED" ]; then
        echo -e "\n${GREEN}============== TEST SEQUENCE COMPLETED SUCCESSFULLY ==============${NC}"
        echo -e "${YELLOW}Final Core Architecture Result Matrix:${NC}"
        # Render the full executive system markdown text summary directly to terminal
        echo "$JOB_STATUS_PAYLOAD" | grep -o '"result":"[^"]*' | sed 's/"result":"//' | sed 's/\\n/\n/g' | sed 's/\\"/"/g'
        break
    elif [ "$STATUS_TOKEN" == "FAILED" ]; then
        echo -e "\n${RED}🚨 Multi-agent pipeline failed in background worker layer.${NC}"
        echo "$JOB_STATUS_PAYLOAD"
        break
    else
        echo -e -n "${YELLOW}. (Multi-Agent Crew running Corrective RAG compliance sweeps)${NC}"
        sleep $DELAY_SECONDS
        RETRY_COUNT=$((RETRY_COUNT+1))
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "\n${RED}🚨 Timeout limit hit. Background pipeline pass exceeded total polling threshold allocation.${NC}"
fi

# Clean exit protocols: kill background server instance if it was spawned locally by this script run context
if [ ! -z "$SERVER_PID" ]; then
    echo -e "${CYAN}Stopping local server background socket...${NC}"
    kill $SERVER_PID
fi
