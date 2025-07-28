"""
Orchestrator API Routes - Explainability & Trace
"""
from fastapi import APIRouter, Query
from typing import List, Optional
from .engine import orchestration_traces

router = APIRouter()

@router.get("/orchestration/traces")
def get_orchestration_traces(
    model: Optional[str] = Query(None, description="Filter by model name"),
    status: Optional[str] = Query(None, description="Filter by status (success/failure/circuit_open/no_healthy_model)"),
    limit: int = Query(20, ge=1, le=100, description="Number of traces to return")
):
    """
    Get recent orchestration traces for explainability and debugging.
    """
    traces = orchestration_traces[-limit:][::-1]  # Most recent first
    if model:
        traces = [t for t in traces if t.get("model") == model]
    if status:
        traces = [t for t in traces if t.get("error") and status in t["error"] or (not t.get("error") and status == "success")]
    return traces
