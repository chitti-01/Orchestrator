from typing import Dict, Any, List, Optional
from orchestrator.core.task_graph import TaskNode, TaskGraph
from orchestrator.context.package import ContextPackage
from orchestrator.context.store import ContextStore
from orchestrator.analysis.requirements import TaskRequirements

class ContextManager:
    def __init__(self, store: Optional[ContextStore] = None):
        self.store = store or ContextStore()

    def build_package_for_node(self, node: TaskNode, graph: TaskGraph, reqs: TaskRequirements) -> ContextPackage:
        # Worker Isolation: Extract ONLY direct dependency outputs from parent nodes
        parent_results: Dict[str, str] = {}
        for dep_id in node.dependencies:
            res = self.store.get_result(dep_id)
            if res:
                dep_node = graph.nodes.get(dep_id)
                dep_name = dep_node.name if dep_node else dep_id
                parent_results[dep_name] = res

        constraints = []
        if reqs.security_critical:
            constraints.append("Enforce strict security and compliance standards.")
        if reqs.testing_requirement >= 0.7:
            constraints.append("Include unit/integration test coverage.")

        return ContextPackage(
            task_id=node.task_id,
            task_name=node.name,
            task_description=node.description,
            relevant_requirements={
                "intent": reqs.intent,
                "target_domain": reqs.target_domain,
                "security_critical": reqs.security_critical
            },
            parent_results=parent_results,
            global_objective=graph.raw_prompt,
            constraints=constraints,
            expected_format=reqs.deliverable_type
        )

    def record_node_result(self, node_id: str, result: str):
        self.store.save_result(node_id, result)
