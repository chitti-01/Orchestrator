from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ModelCapabilities(BaseModel):
    reasoning: float = Field(default=0.5, ge=0.0, le=1.0, description="Logic and reasoning capacity")
    planning: float = Field(default=0.5, ge=0.0, le=1.0, description="Task decomposition and roadmap planning capacity")
    architecture: float = Field(default=0.5, ge=0.0, le=1.0, description="System design and enterprise architecture capacity")
    implementation: float = Field(default=0.5, ge=0.0, le=1.0, description="Software implementation capacity")
    coding: float = Field(default=0.5, ge=0.0, le=1.0, description="Code synthesis and refactoring capacity")
    security: float = Field(default=0.5, ge=0.0, le=1.0, description="Security audit and vulnerability compliance capacity")
    distributed_systems: float = Field(default=0.5, ge=0.0, le=1.0, description="Distributed systems & concurrency capacity")
    data_modeling: float = Field(default=0.5, ge=0.0, le=1.0, description="Data schema and modeling capacity")
    integration: float = Field(default=0.5, ge=0.0, le=1.0, description="System integration and API specification capacity")
    testing: float = Field(default=0.5, ge=0.0, le=1.0, description="Test strategy and test synthesis capacity")
    documentation: float = Field(default=0.5, ge=0.0, le=1.0, description="Technical documentation and writing capacity")
    summarization: float = Field(default=0.5, ge=0.0, le=1.0, description="Text summarization capacity")
    context_handling: float = Field(default=0.5, ge=0.0, le=1.0, description="Large context comprehension capacity")
    tool_use: float = Field(default=0.5, ge=0.0, le=1.0, description="Function calling and tool invocation capacity")
    verification: float = Field(default=0.5, ge=0.0, le=1.0, description="Verification and audit capacity")
    mathematics: float = Field(default=0.5, ge=0.0, le=1.0, description="Formal mathematical proof capacity")
    multimodal: bool = Field(default=False, description="Vision/audio modality support")
    reliability: float = Field(default=0.95, ge=0.0, le=1.0, description="Historical execution success rate")
    context_window: int = Field(default=16000, ge=1000, description="Maximum token context window")

class ModelCost(BaseModel):
    input_per_1k: float = Field(default=0.0, ge=0.0)
    output_per_1k: float = Field(default=0.0, ge=0.0)
