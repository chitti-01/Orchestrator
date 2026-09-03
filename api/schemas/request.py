from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class OrchestratorOptions(BaseModel):
    allow_decomposition: bool = True
    allow_ai_analysis: bool = False
    allow_replanning: bool = True
    max_cost: Optional[float] = None
    max_latency_ms: Optional[float] = None

class OrchestrationAPIRequest(BaseModel):
    prompt: str = Field(..., description="User request prompt or system task")
    options: Optional[OrchestratorOptions] = Field(default_factory=OrchestratorOptions)
