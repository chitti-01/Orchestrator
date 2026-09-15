from pydantic import BaseModel, Field
from typing import List, Optional
from orchestrator.models.capabilities import ModelCapabilities, ModelCost

class ModelCapabilityProfile(BaseModel):
    id: str
    name: str
    tier: str  # "simple", "medium", "complex"
    provider: str = "openai"  # "openai", "anthropic", "google", "groq", "openrouter", "ollama", "mock"
    model_name: str = "gpt-4o-mini"
    api_key_env: Optional[str] = None
    api_base_env: Optional[str] = None
    api_base: Optional[str] = None
    description: Optional[str] = ""
    capabilities: ModelCapabilities
    cost: ModelCost
    latency_class: str = "fast"  # "fast", "balanced", "high_capability"
    specializations: List[str] = Field(default_factory=list)

