from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RoutingDecision(BaseModel):
    selected_model: str            # e.g. "model_2"
    model_name: str                # e.g. "Model 2 (Medium)"
    tier: str                      # e.g. "medium"
    task_complexity: float = 20.0  # TaskComplexity (0.0 to 100.0)
    complexity_score: float = 20.0 # Backwards compatibility alias
    required_capabilities: Dict[str, float] = Field(default_factory=dict)
    model_capabilities: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    eligible_models: List[str] = Field(default_factory=list)
    rejected_models: Dict[str, str] = Field(default_factory=dict)
    rejection_reasons: Dict[str, str] = Field(default_factory=dict)
    capability_gaps: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    capability_match_score: float = 1.0
    cost_score: float = 1.0
    latency_score: float = 1.0
    final_score: float = 1.0
    confidence: float = 0.95
    routing_confidence: float = 0.95
    suitability_score: float = 1.0
    task_type: str = "explain"
    decision_latency_ms: float = 1.0
    ambiguous: bool = False
    selection_reason: str = ""
    reasons: List[str] = Field(default_factory=list)
    alternatives: List[str] = Field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_latency_ms: float = 0.0
