from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class OrchestrationMetrics(BaseModel):
    total_latency_ms: float
    estimated_cost: float

class OrchestrationAPIResponse(BaseModel):
    workflow_id: str
    status: str
    selected_model: str
    workflow_complexity: float = 0.0
    complexity_score: float = 0.0
    confidence: float
    analysis_confidence: Dict[str, Any] = Field(default_factory=dict)
    task_type: str
    deliverable_type: str = "text"
    scope: str = "single_operation"
    explicit_technologies: List[str] = Field(default_factory=list)
    recommended_technologies: List[str] = Field(default_factory=list)
    explicit_exclusions: List[str] = Field(default_factory=list)
    routing_decision: Dict[str, Any]
    routing_audit: List[Dict[str, Any]] = Field(default_factory=list)
    task_complexities: Dict[str, float] = Field(default_factory=dict)
    task_capabilities: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    plan: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    verification_passed: bool
    verification_results: Dict[str, Any] = Field(default_factory=dict)
    recovery_trace: List[Dict[str, Any]] = Field(default_factory=list)
    requirement_coverage: List[Dict[str, Any]] = Field(default_factory=list)
    extracted_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    requirement_graph: Dict[str, Any] = Field(default_factory=dict)
    evidence_trails: Dict[str, Any] = Field(default_factory=dict)
    metrics: OrchestrationMetrics
    events: List[Dict[str, Any]]
