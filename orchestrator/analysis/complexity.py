from typing import Tuple, List, Dict, Any, Optional
from orchestrator.analysis.requirements import TaskRequirements
from orchestrator.policy.engine import PolicyEngine

class ComplexityAnalyzer:
    """
    Multi-Dimensional Complexity Engine with Per-Dimension Evidence Trails.
    Evaluates 16 normalized dimensions (0.0 to 1.0) and non-linear feature interaction effects.
    """
    def __init__(self, policy_engine: Optional[PolicyEngine] = None):
        self.policy_engine = policy_engine or PolicyEngine()
        self.dimension_weights = {
            "reasoning_depth": 0.15,
            "planning_requirement": 0.12,
            "implementation_scope": 0.10,
            "dependency_complexity": 0.09,
            "architecture_complexity": 0.10,
            "integration_complexity": 0.06,
            "context_requirement": 0.04,
            "ambiguity": 0.04,
            "constraint_density": 0.05,
            "tool_requirement": 0.05,
            "statefulness": 0.03,
            "scale_requirement": 0.04,
            "reliability_requirement": 0.04,
            "security_requirement": 0.04,
            "testing_requirement": 0.02,
            "output_complexity": 0.03
        }

    def compute_complexity_with_evidence(self, reqs: TaskRequirements) -> Tuple[float, List[str], Dict[str, Dict[str, Any]]]:
        signals: List[str] = []
        evidence_trails: Dict[str, Dict[str, Any]] = {}
        lower_prompt = reqs.raw_prompt.lower()

        # Build evidence trails for each dimension
        dim_values = {
            "reasoning_depth": (reqs.reasoning_depth, self._extract_evidence("reasoning", reqs, lower_prompt)),
            "planning_requirement": (reqs.planning_requirement, self._extract_evidence("planning", reqs, lower_prompt)),
            "implementation_scope": (reqs.implementation_scope, self._extract_evidence("implementation", reqs, lower_prompt)),
            "dependency_complexity": (reqs.dependency_complexity, self._extract_evidence("dependency", reqs, lower_prompt)),
            "architecture_complexity": (reqs.architecture_complexity, self._extract_evidence("architecture", reqs, lower_prompt)),
            "integration_complexity": (reqs.integration_complexity, self._extract_evidence("integration", reqs, lower_prompt)),
            "context_requirement": (reqs.context_requirement, self._extract_evidence("context", reqs, lower_prompt)),
            "ambiguity": (reqs.ambiguity, self._extract_evidence("ambiguity", reqs, lower_prompt)),
            "constraint_density": (reqs.constraint_density, self._extract_evidence("constraints", reqs, lower_prompt)),
            "tool_requirement": (reqs.tool_requirement, self._extract_evidence("tool", reqs, lower_prompt)),
            "statefulness": (reqs.statefulness, self._extract_evidence("statefulness", reqs, lower_prompt)),
            "scale_requirement": (reqs.scale_requirement, self._extract_evidence("scale", reqs, lower_prompt)),
            "reliability_requirement": (reqs.reliability_requirement, self._extract_evidence("reliability", reqs, lower_prompt)),
            "security_requirement": (reqs.security_requirement, self._extract_evidence("security", reqs, lower_prompt)),
            "testing_requirement": (reqs.testing_requirement, self._extract_evidence("testing", reqs, lower_prompt)),
            "output_complexity": (reqs.output_complexity, self._extract_evidence("output", reqs, lower_prompt))
        }

        base_sum = 0.0
        total_weight = 0.0
        for dim, (score, ev_list) in dim_values.items():
            w = self.dimension_weights.get(dim, 0.05)
            base_sum += score * w
            total_weight += w
            evidence_trails[dim] = {
                "score": round(score, 2),
                "evidence": ev_list
            }

        normalized_base = (base_sum / total_weight) if total_weight > 0 else 0.2

        # Feature Interaction Effects
        interaction_bonus = 0.0
        if reqs.planning_requirement >= 0.7 and reqs.dependency_complexity >= 0.7:
            interaction_bonus += 0.12
            signals.append("Feature Interaction: High planning x dependency complexity")

        if reqs.architecture_complexity >= 0.7 and reqs.scale_requirement >= 0.7:
            interaction_bonus += 0.10
            signals.append("Feature Interaction: Enterprise architecture x high-scale requirement")

        if reqs.reasoning_depth >= 0.8 and reqs.constraint_density >= 0.6:
            interaction_bonus += 0.10
            signals.append("Feature Interaction: Deep reasoning x high constraint density")

        if reqs.implementation_scope >= 0.7 and reqs.integration_complexity >= 0.6:
            interaction_bonus += 0.08
            signals.append("Feature Interaction: Broad implementation scope x multi-service integration")

        # Informational Hard Cap
        if not reqs.is_actionable and reqs.intent in ["explain", "query_info", "summarize"]:
            raw_total = min(normalized_base, 0.30)
            final_score = round(raw_total * 100.0, 1)
            signals.append("Informational Query: Complexity capped for non-actionable query")
            return final_score, signals, evidence_trails

        total_normalized = min(normalized_base + interaction_bonus, 1.0)
        final_score = round(total_normalized * 100.0, 1)

        if not signals:
            if final_score <= 32.0:
                signals.append("Baseline routine task execution")
            elif final_score <= 68.0:
                signals.append("Moderate task complexity requiring structured execution")
            else:
                signals.append("High task complexity requiring frontier model planning & decomposition")

        return final_score, signals, evidence_trails

    def compute_complexity(self, reqs: TaskRequirements) -> Tuple[float, List[str]]:
        score, signals, _ = self.compute_complexity_with_evidence(reqs)
        return score, signals

    def _extract_evidence(self, dim: str, reqs: TaskRequirements, lower: str) -> List[str]:
        evidence = []
        if dim == "reasoning" and reqs.reasoning_depth >= 0.6:
            evidence.append(f"Intent '{reqs.intent}' requires deep logic analysis")
            if "distributed" in lower: evidence.append("Distributed consistency logic")
            if "proof" in lower: evidence.append("Formal mathematical theorem proof")
        elif dim == "architecture" and reqs.architecture_complexity >= 0.6:
            evidence.append("Multi-component architectural boundaries")
            if "multi-region" in lower: evidence.append("Multi-region deployment requirement")
        elif dim == "security" and reqs.security_requirement >= 0.6:
            evidence.append("Security isolation or authorization compliance")
            if "pci" in lower: evidence.append("PCI-DSS Level 1 compliance")
            if "tenant" in lower: evidence.append("Multi-tenant permission-aware data isolation")
        elif dim == "scale" and reqs.scale_requirement >= 0.6:
            evidence.append("High throughput or scaling requirement")
            if "concurrent" in lower: evidence.append("Concurrent execution & rate limits")
        else:
            evidence.append(f"Dimension '{dim}' evaluated from requirement signals")
        return evidence
