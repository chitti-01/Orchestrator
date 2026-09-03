from pydantic import BaseModel, Field
from typing import List, Optional
from orchestrator.models.capabilities import ModelCapabilities, ModelCost

class ModelCapabilityProfile(BaseModel):
    id: str
    name: str
    tier: str  # "simple", "medium", "complex"
    description: Optional[str] = ""
    capabilities: ModelCapabilities
    cost: ModelCost
    latency_class: str = "fast"  # "fast", "balanced", "high_capability"
    specializations: List[str] = Field(default_factory=list)
