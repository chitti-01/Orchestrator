from typing import List, Dict, Any, Optional, Tuple
from orchestrator.analysis.requirements import TaskRequirements, RequirementItem
from orchestrator.analysis.requirement_graph import RequirementGraph
from orchestrator.core.task_graph import TaskGraph, TaskNode

class TaskDecomposer:
    """
    V5 Requirement-Driven DAG Task Decomposer.
    Generates dynamic DAG nodes with independent per-task capability requirement vectors,
    task complexities, and criticalities.
    Enforces Rule 1 (Workflow Complexity != Task Complexity) and Rule 3 (Capability Vector Routing).
    """
    def decompose(self, reqs: TaskRequirements, req_graph: Optional[RequirementGraph] = None) -> TaskGraph:
        graph = TaskGraph(raw_prompt=reqs.raw_prompt)

        # Single Task Prompt Detection (Q&A, simple explanations, basic code operations, single proofs)
        if reqs.can_solve_directly or (len(reqs.extracted_requirements) <= 1 and not reqs.system_architecture and reqs.scope != "complete_system"):
            task_caps = self._build_single_task_caps(reqs)
            task_comp = 15.0 if not reqs.is_actionable else (95.0 if reqs.formal_proof else 50.0)
            
            single_node = TaskNode(
                name="Main Execution Task",
                description=f"Execute request: {reqs.raw_prompt}",
                source_requirements=[r.id for r in reqs.extracted_requirements],
                requirements=[r.id for r in reqs.extracted_requirements],
                dependencies=[],
                required_capabilities=task_caps,
                task_complexity=task_comp,
                node_complexity=task_comp,
                criticality="critical" if reqs.formal_proof else ("high" if reqs.security_critical else "medium"),
                context_requirement=0.05
            )
            graph.add_node(single_node)
            graph.execution_order = [single_node.task_id]
            return graph

        # Multi-Requirement Prompt -> Dynamic Requirement-Derived DAG Tasks (R1..Rn)
        items = reqs.extracted_requirements
        created_nodes: List[TaskNode] = []
        created_node_ids: List[str] = []

        # Root Node: Establishing Architecture & Constraint Boundaries (Model 3 for distributed systems)
        root_caps = {
            "reasoning": 0.90,
            "architecture": 0.95,
            "planning": 0.90,
            "distributed_systems": 0.85 if reqs.system_architecture else 0.40
        }
        root_node = TaskNode(
            name="Define Architecture & Objective Boundaries",
            description=f"Establish architectural baseline and explicit constraint boundaries for: {reqs.raw_prompt}",
            source_requirements=[],
            requirements=[],
            dependencies=[],
            required_capabilities=root_caps,
            task_complexity=90.0 if reqs.system_architecture else 65.0,
            node_complexity=90.0 if reqs.system_architecture else 65.0,
            criticality="high",
            context_requirement=0.15
        )
        graph.add_node(root_node)
        created_node_ids.append(root_node.task_id)

        # Dynamic Requirement Tasks
        req_node_map: Dict[str, str] = {}

        for item in items:
            task_name = f"Satisfy {item.description.replace('Requirement: ', '').title()}"
            task_desc = f"Address requirement '{item.description}': Category={item.category}, Criticality={item.criticality}"

            deps = [root_node.task_id]
            for parent_req_id in item.dependencies:
                if parent_req_id in req_node_map:
                    deps.append(req_node_map[parent_req_id])

            task_caps, task_comp, criticality = self._derive_task_capabilities(item, reqs)

            node = TaskNode(
                name=task_name,
                description=task_desc,
                source_requirements=[item.id],
                requirements=[item.id],
                dependencies=deps,
                required_capabilities=task_caps,
                task_complexity=task_comp,
                node_complexity=task_comp,
                criticality=criticality,
                context_requirement=0.08
            )
            graph.add_node(node)
            created_nodes.append(node)
            created_node_ids.append(node.task_id)
            req_node_map[item.id] = node.task_id

        # Standard API / Interface Component Task (Model 2)
        if reqs.scope in ["complete_system", "multiple_components"] or reqs.is_actionable:
            api_node = TaskNode(
                name="Define REST Endpoint Specifications & Interfaces",
                description="Specify API endpoints, request/response payload schemas, and client interaction contracts.",
                source_requirements=[],
                requirements=[],
                dependencies=[root_node.task_id],
                required_capabilities={
                    "implementation": 0.75,
                    "coding": 0.80,
                    "integration": 0.75,
                    "data_modeling": 0.70
                },
                task_complexity=50.0,
                node_complexity=50.0,
                criticality="medium",
                context_requirement=0.10
            )
            graph.add_node(api_node)
            created_nodes.append(api_node)
            created_node_ids.append(api_node.task_id)

        # System Observability & User Documentation Task (Model 1)
        doc_node = TaskNode(
            name="Technical Documentation & Observability Metrics",
            description="Document system architecture, API specifications, operational runbooks, and list observability metrics.",
            source_requirements=[],
            requirements=[],
            dependencies=[n.task_id for n in created_nodes if n.task_id != root_node.task_id] or [root_node.task_id],
            required_capabilities={
                "documentation": 0.80,
                "summarization": 0.85,
                "implementation": 0.35,
                "testing": 0.35
            },
            task_complexity=20.0,
            node_complexity=20.0,
            criticality="low",
            context_requirement=0.05
        )
        graph.add_node(doc_node)
        created_nodes.append(doc_node)
        created_node_ids.append(doc_node.task_id)

        # Integration & Verification Final Node (Model 2/3)
        final_caps = {
            "verification": 0.85,
            "architecture": 0.80,
            "testing": 0.80,
            "reasoning": 0.75
        }
        final_node = TaskNode(
            name="System Integration & Requirement Verification",
            description=f"Integrate architectural decisions and verify satisfaction across all {len(items)} requirements",
            source_requirements=[r.id for r in items],
            requirements=[r.id for r in items],
            dependencies=[n.task_id for n in created_nodes],
            required_capabilities=final_caps,
            task_complexity=75.0,
            node_complexity=75.0,
            criticality="high",
            context_requirement=0.20
        )
        graph.add_node(final_node)
        created_node_ids.append(final_node.task_id)

        graph.execution_order = created_node_ids
        return graph

    def _build_single_task_caps(self, reqs: TaskRequirements) -> Dict[str, float]:
        raw_lower = reqs.raw_prompt.lower()
        words = raw_lower.split()

        if reqs.intent in ["explain", "summarize"] or not reqs.is_actionable or "handshake" in raw_lower or "what is" in raw_lower or "binary search" in raw_lower:
            return {
                "reasoning": 0.25,
                "documentation": 0.80,
                "summarization": 0.85,
                "coding": 0.20,
                "implementation": 0.20
            }
        elif reqs.intent == "prove":
            return {
                "reasoning": 0.98,
                "mathematics": 0.95,
                "planning": 0.85
            }
        elif "reverse" in raw_lower or "hello world" in raw_lower:
            return {
                "coding": 0.40,
                "implementation": 0.40,
                "reasoning": 0.30,
                "documentation": 0.50
            }
        elif reqs.is_actionable or "build" in raw_lower or "payment" in raw_lower or "rest api" in raw_lower:
            return {
                "coding": 0.75,
                "implementation": 0.75,
                "integration": 0.70,
                "reasoning": 0.65
            }
        else:
            return {
                "coding": 0.40,
                "implementation": 0.45,
                "reasoning": 0.35,
                "documentation": 0.75
            }

    def _derive_task_capabilities(self, item: RequirementItem, reqs: TaskRequirements) -> Tuple[Dict[str, float], float, str]:
        desc_lower = item.description.lower()
        cat = item.category.lower()

        if "security" in cat or "pci" in desc_lower or "tenant" in desc_lower or "authorization" in desc_lower:
            return {
                "security": 0.92,
                "architecture": 0.85,
                "reasoning": 0.80,
                "implementation": 0.70
            }, 85.0, "critical"

        elif "concurrency" in desc_lower or "transaction" in desc_lower or "partition" in desc_lower or "failover" in desc_lower or "recovery" in desc_lower or "edits" in desc_lower:
            return {
                "distributed_systems": 0.92,
                "reasoning": 0.90,
                "architecture": 0.85,
                "testing": 0.60
            }, 92.0, "critical"

        elif "scaling" in desc_lower or "scale" in cat:
            return {
                "distributed_systems": 0.75,
                "architecture": 0.70,
                "implementation": 0.70,
                "reasoning": 0.65
            }, 65.0, "high"

        elif "testing" in cat or "testing strategy" in desc_lower or "test" in desc_lower:
            return {
                "testing": 0.80,
                "documentation": 0.75,
                "summarization": 0.70,
                "implementation": 0.40
            }, 35.0, "medium"

        elif "observability" in desc_lower or "metrics" in desc_lower or "logging" in desc_lower or "documentation" in desc_lower:
            return {
                "documentation": 0.80,
                "summarization": 0.85,
                "implementation": 0.35,
                "testing": 0.40
            }, 20.0, "low"

        else:
            return {
                "implementation": 0.75,
                "coding": 0.75,
                "integration": 0.70,
                "data_modeling": 0.70
            }, 55.0, "medium"
