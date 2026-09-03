from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ContextPackage(BaseModel):
    task_id: str
    task_name: str
    task_description: str
    relevant_requirements: Dict[str, Any] = Field(default_factory=dict)
    parent_results: Dict[str, str] = Field(default_factory=dict) # Dependency outputs only
    global_objective: str
    constraints: List[str] = Field(default_factory=list)
    expected_format: str = "text"
    system_prompt: str = "You are an isolated task worker inside an AI orchestration pipeline."
