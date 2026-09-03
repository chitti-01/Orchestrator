from typing import List, Dict, Any
from orchestrator.core.task_graph import TaskGraph, TaskNode
from orchestrator.recovery.escalation import EscalationManager

class Replanner:
    """
    Failure Cause Classification and Closed-Loop Recovery Manager.
    """
    def __init__(self):
        self.escalator = EscalationManager()
        self.max_retries = 3

    def classify_failure(self, node: TaskNode) -> str:
        if not node.result:
            return "transient_failure"
        if "insufficient" in node.result.lower() or "capability" in node.result.lower():
            return "insufficient_model_capability"
        if "context" in node.result.lower() or "missing" in node.result.lower():
            return "missing_context"
        return "verification_failure"

    def replan_failed_nodes(self, graph: TaskGraph, failed_nodes: List[TaskNode]) -> bool:
        replanned_any = False

        for node in failed_nodes:
            if node.retry_count >= self.max_retries:
                continue

            failure_cause = self.classify_failure(node)
            node.retry_count += 1

            if failure_cause == "insufficient_model_capability" or node.retry_count >= 2:
                # Escalate model tier
                self.escalator.escalate_node(node)
            
            # Reset for re-execution
            node.status = "pending"
            node.verification_status = "unverified"
            replanned_any = True

        return replanned_any
