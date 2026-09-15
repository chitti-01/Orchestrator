import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TaskNode(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    name: str
    description: str
    source_requirements: List[str] = Field(default_factory=list) # Requirement IDs (R1, R2...)
    requirements: List[str] = Field(default_factory=list) # Backwards compatibility alias
    task_complexity: float = 20.0
    node_complexity: float = 20.0 # Backwards compatibility alias
    criticality: str = "medium"  # low, medium, high, critical
    required_capabilities: Dict[str, float] = Field(default_factory=dict) # capability vector (e.g. {"reasoning": 0.85, ...})
    capability_scores: Dict[str, float] = Field(default_factory=dict) # scores per model
    eligible_models: List[str] = Field(default_factory=list) # e.g. ["model_2", "model_3"]
    rejected_models: Dict[str, str] = Field(default_factory=dict) # e.g. {"model_1": "insufficient distributed_systems"}
    capability_gaps: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict) # per model list of gap objects
    selected_model: str = "model_1"
    selection_reason: str = "Default assignment"
    routing_confidence: float = 0.90
    estimated_cost: float = 0.0
    estimated_latency: float = 0.0
    context_requirement: float = 0.20
    minimum_model_tier: str = "model_1"
    dependencies: List[str] = Field(default_factory=list) # Task IDs of parent dependencies
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[str] = None
    retry_count: int = 0
    verification_status: str = "unverified"  # unverified, passed, failed
    execution_time_ms: float = 0.0
    provider: Optional[str] = None
    actual_model_name: Optional[str] = None
    tokens_used: int = 0
    execution_error: Optional[str] = None


class TaskGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: f"wf_{uuid.uuid4().hex[:8]}")
    raw_prompt: str
    nodes: Dict[str, TaskNode] = Field(default_factory=dict)
    execution_order: List[str] = Field(default_factory=list)

    def add_node(self, node: TaskNode):
        self.nodes[node.task_id] = node

    def get_ready_nodes(self) -> List[TaskNode]:
        """Returns all pending nodes whose dependencies are all completed."""
        ready = []
        for node in self.nodes.values():
            if node.status == "pending":
                deps_met = all(
                    self.nodes[dep_id].status == "completed"
                    for dep_id in node.dependencies
                    if dep_id in self.nodes
                )
                if deps_met:
                    ready.append(node)
        return ready

    def is_complete(self) -> bool:
        return all(node.status in ["completed", "failed"] for node in self.nodes.values())

    def has_failures(self) -> bool:
        return any(node.status == "failed" for node in self.nodes.values())
