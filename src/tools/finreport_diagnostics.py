from __future__ import annotations
import os
import re
import json
import logging
from typing import Any, List, Dict
from crewai.tools import tool
from pydantic import BaseModel, Field

logger = logging.getLogger("EPM_Orchestrator_FinReport_Diagnostics")

# --- CONSOLIDATED ENTERPRISE FILTER REGISTRY ---
PAX_ERROR_PATTERNS: tuple[tuple[str, str, str], ...] = (
    ("blank_task_pane", r"(pax|pafe).{0,40}(blank|empty|not\s+responding)", "PAX task pane is blank or unresponsive."),
    ("mdx_timeout", r"(mdx|view).{0,40}(timeout|timed\s+out|time[\s-]?out)", "MDX view or query timed out."),
    ("writeback_failure", r"(write[\s-]?back|cell\s+update).{0,40}(fail|denied|error)", "Cube writeback or cell update failed."),
    ("connection_drop", r"(tm1|pax|pafe).{0,40}(disconnect|connection\s+(lost|drop)|not\s+connected)", "TM1/PAX connection dropped."),
    ("macro_conflict", r"(macro|vba|add[\s-]?in).{0,40}(conflict|disabled|crash)", "Excel macro or add-in conflict."),
    ("auth_failure", r"(unauthori[sz]ed|login\s+failed|invalid\s+(token|credential)|401|403)", "Authentication or authorization failed."),
    ("dimension_mismatch", r"(dimension|hierarchy|subset).{0,40}(mismatch|not\s+found|invalid)", "Dimension, hierarchy, or subset is misaligned."),
    ("currency_translation", r"(fx|currency|translation).{0,40}(fail|error|missing)", "Multi-currency translation error."),
)

MDX_BLOCK = re.compile(r"(?is)(?:mdx\s*[:=]\s*)?(select\s+.*?from\s+\[[^\]]+\](?:\s+where\s+.*)?)(?:;|\n|$)")
CUBE_REF = re.compile(r"\[[^\]]+\]")
TM1_FORMULA = re.compile(r"(?i)(TM1RPTVIEW|DBRW|DBS|DBRA|SUBNM|VIEW)\s*\(([^)]*)\)")
EXCEL_CELL = re.compile(r"\b([A-Z]{1,3}\d{1,7})\b")

PORTFOLIO_KEYWORDS: dict[str, tuple[str, ...]] = {
    "quarterly_close": ("close", "q1", "q2", "q3", "q4", "rollup", "consolidation"),
    "underwriting": ("underwrite", "noi", "cap rate", "dscr", "irr", "pro forma"),
    "portfolio_valuation": ("valuation", "nav", "mark-to-market", "appraisal", "asset"),
    "fx_reporting": ("fx", "currency", "translation", "usd", "eur", "gbp"),
}
PRIORITY_ORDER = ("quarterly_close", "underwriting", "portfolio_valuation", "fx_reporting")

# --- CORE UTILITY HELPER METHODS ---
def _match_patterns(text: str) -> list[dict[str, str]]:
    haystack = text.lower()
    hits: list[dict[str, str]] = []
    for code, pattern, summary in PAX_ERROR_PATTERNS:
        if re.search(pattern, haystack, flags=re.IGNORECASE | re.DOTALL):
            hits.append({"code": code, "summary": summary})
    return hits

def _extract_mdx(text: str) -> list[str]:
    queries = [m.group(1).strip() for m in MDX_BLOCK.finditer(text)]
    seen: set[str] = set()
    unique: list[str] = []
    for query in queries:
        key = re.sub(r"\s+", " ", query.lower())
        if key not in seen:
            seen.add(key)
            unique.append(query)
    return unique

def _extract_formulas(text: str) -> list[dict[str, str]]:
    return [
        {"function": match.group(1).upper(), "args": match.group(2).strip()}
        for match in TM1_FORMULA.finditer(text)
    ]

# --- PYDANTIC INTERACTION SCHEMAS ---
class RegexSchema(BaseModel):
    telemetry: str = Field(..., description="Raw unstructured client-side PAX/PAfE Excel logs or Windows event text.")

class MdxSchema(BaseModel):
    telemetry: str = Field(..., description="Raw text containing queries or cube strings.")

class MetadataSchema(BaseModel):
    fault_context: str = Field(..., description="Structured output parser data or a summary problem statement.")

# --- TOOL IMPLEMENTATION ACTIONS ---
@tool("regex_tool", args_schema=RegexSchema)
def regex_tool(telemetry: str) -> str:
    """Parse unstructured PAX/PAfE Excel logs or Windows event text.
    Extracts known error codes, TM1 worksheet formulas, Excel cell refs,
    and a short impact hint. Use this first on raw client telemetry.
    """
    logger.info("⚙️ Running analytical regex parsing metrics across unstructured trace input.")
    matches = _match_patterns(telemetry)
    formulas = _extract_formulas(telemetry)
    cells = sorted(set(EXCEL_CELL.findall(telemetry)))
    
    payload: dict[str, Any] = {
        "error_matches": matches,
        "primary_fault": matches[0]["code"] if matches else "unclassified",
        "tm1_formulas": formulas,
        "excel_cells": cells[:50],
        "severity": "high" if matches else "unknown",
    }
    return json.dumps(payload, indent=2)

@tool("mdx_tool", args_schema=MdxSchema)
def mdx_tool(telemetry: str) -> str:
    """Extract nested MDX queries and cube/dimension tokens from telemetry.
    Use when logs contain SELECT ... FROM [Cube] statements or TM1 view names.
    """
    logger.info("⚙️ Extracting discrete MDX dimensional axes strings.")
    queries = _extract_mdx(telemetry)
    cubes: list[str] = []
    for query in queries:
        cubes.extend(CUBE_REF.findall(query))
    fault_codes = {m["code"] for m in _match_patterns(telemetry)}
    
    payload = {
        "mdx_queries": queries,
        "cube_or_dimension_tokens": sorted(set(cubes)),
        "query_count": len(queries),
        "likely_timeout": "mdx_timeout" in fault_codes,
    }
    return json.dumps(payload, indent=2)

@tool("metadata_tool", args_schema=MetadataSchema)
def metadata_tool(fault_context: str) -> str:
    """Map a technical PAX/TM1 fault to CRE underwriting and close-cycle risk.
    Pass structured parser output or a short problem statement. Returns the
    matched financial workflow, priority, and TM1 instance from the environment.
    """
    logger.info("⚙️ Running underwriting materiality and close-cycle risk scoring pass.")
    lowered = fault_context.lower()
    matched_workflows = [
        name for name, keywords in PORTFOLIO_KEYWORDS.items()
        if any(keyword in lowered for keyword in keywords)
    ]
    if not matched_workflows:
        matched_workflows = ["general_reporting"]
        
    priority = "P2"
    for name in PRIORITY_ORDER:
        if name in matched_workflows:
            priority = "P1"
            break
            
    payload = {
        "workflows": matched_workflows,
        "priority": priority,
        "tm1_instance": os.getenv("TM1_INSTANCE_NAME", "CXMD"),
        "tm1_rest_api_url": os.getenv("TM1_REST_API_URL", ""),
        "business_impact": (
            "Blocks active underwriting or quarterly close reporting."
            if priority == "P1"
            else "Degrades reporting; contain before the next close cycle."
        ),
    }
    return json.dumps(payload, indent=2)
