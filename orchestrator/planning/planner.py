import time
from typing import Tuple, List, Optional
from orchestrator.analysis.requirements import TaskRequirements
from orchestrator.analysis.requirement_graph import RequirementGraph
from orchestrator.planning.decomposer import TaskDecomposer
from orchestrator.core.task_graph import TaskGraph
from orchestrator.routing.router import ModelRouter

class TaskPlanner:
    """
    V5 Requirement-Driven Workflow Planner.
    Decomposes requirements into DAG task graph and assigns optimal model tier PER TASK NODE
    by evaluating per-task capability requirements against model capability vectors (Rule 1 & Rule 3).
    """
    def __init__(self, router: Optional[ModelRouter] = None):
        self.decomposer = TaskDecomposer()
        self.router = router or ModelRouter()

    def plan_workflow(
        self,
        reqs: TaskRequirements,
        workflow_score: float,
        workflow_signals: List[str],
        req_graph: Optional[RequirementGraph] = None
    ) -> Tuple[TaskGraph, float]:
        t0 = time.perf_counter()

        # Step 1: Decompose into Requirement-Driven DAG TaskGraph
        graph = self.decomposer.decompose(reqs, req_graph)

        # Step 2: Per-Task Model Selection & Capability Matching (Rule 1, 3, 5, 6, 8)
        for node in graph.nodes.values():
            decision = self.router.route_task(
                task_name=node.name,
                task_description=node.description,
                required_capabilities=node.required_capabilities,
                task_complexity=node.task_complexity,
                criticality=node.criticality,
                context_requirement=node.context_requirement
            )

            # Store per-task decision outcome in TaskNode
            node.selected_model = decision.selected_model
            node.selection_reason = decision.selection_reason
            node.eligible_models = decision.eligible_models
            node.rejected_models = decision.rejected_models
            node.capability_gaps = decision.capability_gaps
            node.capability_scores = decision.capability_match_score if isinstance(decision.capability_match_score, dict) else {decision.selected_model: decision.capability_match_score}
            node.routing_confidence = decision.routing_confidence
            node.estimated_cost = decision.estimated_cost
            node.estimated_latency = decision.estimated_latency_ms

        planning_latency_ms = (time.perf_counter() - t0) * 1000.0
        return graph, round(planning_latency_ms, 3)
