from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from orchestrator.core.task_graph import TaskNode, TaskGraph
from orchestrator.analysis.requirements import TaskRequirements, RequirementItem

class RequirementCoverage(BaseModel):
    req_id: str
    description: str
    category: str
    status: str = "SATISFIED" # SATISFIED, PARTIALLY_SATISFIED, UNSATISFIED
    evidence: str = "Requirement satisfied in workflow output deliverables"

class VerificationResult(BaseModel):
    passed: bool
    reasons: List[str]
    suggested_action: str = "pass"  # pass, retry, escalate, replan
    coverage: List[RequirementCoverage] = Field(default_factory=list)

class Verifier:
    """
    Requirement Coverage Verification Engine validating task deliverables against extracted requirements (R1..Rn).
    """
    def verify_workflow(self, graph: TaskGraph, reqs: TaskRequirements) -> VerificationResult:
        reasons = []
        coverage_list: List[RequirementCoverage] = []
        all_nodes_completed = True

        for node in graph.nodes.values():
            if node.status != "completed" or not node.result:
                all_nodes_completed = False
                reasons.append(f"Node '{node.name}' incomplete or failed execution")

        all_reqs_satisfied = True
        for req_item in reqs.extracted_requirements:
            req_clean = req_item.description.replace("Requirement: ", "").lower()
            matching_output = [
                node.result for node in graph.nodes.values()
                if node.status == "completed" and (req_clean in node.description.lower() or req_clean in node.result.lower())
            ]
            
            if matching_output or reqs.can_solve_directly:
                req_item.satisfied = True
                coverage_list.append(RequirementCoverage(
                    req_id=req_item.id,
                    description=req_item.description,
                    category=req_item.category,
                    status="SATISFIED",
                    evidence=f"Verified satisfaction for {req_item.id} in task deliverables"
                ))
            else:
                req_item.satisfied = False
                all_reqs_satisfied = False
                coverage_list.append(RequirementCoverage(
                    req_id=req_item.id,
                    description=req_item.description,
                    category=req_item.category,
                    status="UNSATISFIED",
                    evidence=f"Unaddressed requirement {req_item.id} in task deliverables"
                ))
                reasons.append(f"Requirement '{req_item.description}' ({req_item.id}) unsatisfied")

        passed = all_nodes_completed and all_reqs_satisfied
        action = "pass" if passed else ("replan" if not all_reqs_satisfied else "retry")

        return VerificationResult(
            passed=passed,
            reasons=reasons if reasons else ["All requirements satisfied successfully"],
            suggested_action=action,
            coverage=coverage_list
        )

    def verify_node(self, node: TaskNode, reqs: TaskRequirements) -> VerificationResult:
        if node.status != "completed" or not node.result:
            return VerificationResult(
                passed=False,
                reasons=[f"Task execution failed or returned empty result for '{node.name}'"],
                suggested_action="retry"
            )
        node.verification_status = "passed"
        return VerificationResult(
            passed=True,
            reasons=["Node verification passed"],
            suggested_action="pass"
        )
