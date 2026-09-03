import time
from typing import List, Tuple, Dict, Any, Optional
from orchestrator.analysis.requirements import TaskRequirements
from orchestrator.routing.decision import RoutingDecision
from orchestrator.routing.capability_matcher import CapabilityMatcher
from orchestrator.models.registry import ModelRegistry
from orchestrator.models.profile import ModelCapabilityProfile
from orchestrator.policy.engine import PolicyEngine

class ModelRouter:
    """
    V5 Model-Agnostic Capability-Based Router.
    Enforces Rule 1 (Workflow Complexity != Task Complexity), Rule 2 (No Keyword Model Routing),
    Rule 5 (Eligibility Before Selection), Rule 6 (Capability Gap Analysis), and Rule 8 (Cost-Aware Selection).
    """
    def __init__(self, registry: Optional[ModelRegistry] = None, policy_engine: Optional[PolicyEngine] = None):
        self.registry = registry or ModelRegistry()
        self.policy_engine = policy_engine or PolicyEngine()
        self.matcher = CapabilityMatcher(self.registry, self.policy_engine)

    def route_task(
        self,
        task_name: str,
        task_description: str,
        required_capabilities: Dict[str, float],
        task_complexity: float = 20.0,
        criticality: str = "medium",
        context_requirement: float = 0.20
    ) -> RoutingDecision:
        t0 = time.perf_counter()

        # Step 1 & 2: Capability Vector Evaluation & Gap Analysis & Eligibility Filtering (Rule 5 & 6)
        match_result = self.matcher.evaluate_task(
            required_capabilities=required_capabilities,
            criticality=criticality,
            context_requirement=context_requirement
        )

        eligible = match_result.eligible_models
        rejected = match_result.rejected_models
        scores = match_result.scores
        gaps = match_result.gaps

        # Step 3: Cost-Aware Model Selection (Rule 8: Select CHEAPEST eligible model)
        models_map = self.registry.list_models()
        tier_cost_rank = {"simple": 1, "medium": 2, "complex": 3}

        sorted_eligible = sorted(
            eligible,
            key=lambda m_id: (
                models_map[m_id].cost.input_per_1k + models_map[m_id].cost.output_per_1k
                if m_id in models_map else tier_cost_rank.get(m_id, 99)
            )
        )

        selected_id = sorted_eligible[0] if sorted_eligible else "model_3"
        selected_model = self.registry.get_model(selected_id) or self.registry.get_model("model_2")

        # Construct Mathematical Selection Rationale (No Fake Reasons)
        reasons_list = []
        if selected_id == "model_1":
            sel_reason = f"MODEL_1 selected: lowest-cost model satisfying capability vector requirements (match score: {scores.get('model_1', 1.0):.2f})."
        elif selected_id == "model_2":
            if "model_1" in rejected:
                rej_m1_reason = rejected["model_1"]
                sel_reason = f"MODEL_2 selected: lowest-cost eligible model (match score: {scores.get('model_2', 1.0):.2f}). MODEL_1 rejected due to {rej_m1_reason}."
            else:
                sel_reason = f"MODEL_2 selected: optimal balance of capability and cost for required capabilities."
        else:
            rejected_summary = []
            if "model_1" in rejected: rejected_summary.append(f"MODEL_1 ({rejected['model_1']})")
            if "model_2" in rejected: rejected_summary.append(f"MODEL_2 ({rejected['model_2']})")
            rej_str = "; ".join(rejected_summary) if rejected_summary else "lower tiers exceeded capability gap thresholds"
            sel_reason = f"MODEL_3 selected: lowest-cost model satisfying high capability requirements. Rejected: {rej_str}."

        reasons_list.append(sel_reason)

        # Estimate Cost & Latency for selected model
        tok_est = int(len(task_description.split()) * 2.0) + 500
        est_cost = selected_model.cost.input_per_1k * (tok_est / 1000.0) + selected_model.cost.output_per_1k * 0.5
        est_lat = 15.0 if selected_model.tier == "simple" else (45.0 if selected_model.tier == "medium" else 90.0)

        latency_ms = (time.perf_counter() - t0) * 1000.0

        alternatives = [m.name for m in models_map.values() if m.id != selected_model.id]

        confidence = self._calculate_confidence(scores.get(selected_id, 0.90), len(eligible), criticality)

        return RoutingDecision(
            selected_model=selected_model.id,
            model_name=selected_model.name,
            tier=selected_model.tier,
            task_complexity=task_complexity,
            complexity_score=task_complexity,
            required_capabilities=required_capabilities,
            model_capabilities=match_result.model_caps,
            eligible_models=eligible,
            rejected_models=rejected,
            rejection_reasons=rejected,
            capability_gaps=gaps,
            capability_match_score=scores.get(selected_id, 0.90),
            cost_score=round(selected_model.cost.input_per_1k, 4),
            latency_score=round(est_lat, 1),
            final_score=scores.get(selected_id, 0.90),
            confidence=confidence,
            routing_confidence=confidence,
            suitability_score=scores.get(selected_id, 0.90),
            task_type=task_name,
            decision_latency_ms=round(latency_ms, 3),
            ambiguous=len(eligible) > 1,
            selection_reason=sel_reason,
            reasons=reasons_list,
            alternatives=alternatives,
            estimated_cost=round(est_cost, 4),
            estimated_latency_ms=est_lat
        )

    def route(self, reqs: TaskRequirements, workflow_complexity_score: float, complexity_signals: List[str]) -> RoutingDecision:
        """
        Backwards-compatible entrypoint mapping task requirements to route_task.
        Note: workflow_complexity_score is logged for audit but NEVER forces task model tier!
        """
        # Convert TaskRequirements to task capability requirements vector
        task_caps = {
            "reasoning": reqs.reasoning_depth,
            "planning": reqs.planning_requirement,
            "architecture": reqs.architecture_complexity,
            "implementation": reqs.implementation_scope,
            "coding": reqs.implementation_scope if reqs.deliverable_type in ["code", "API"] else 0.30,
            "security": reqs.security_requirement,
            "distributed_systems": 0.90 if reqs.system_architecture else 0.20,
            "testing": reqs.testing_requirement,
            "documentation": 0.80 if reqs.intent in ["explain", "summarize"] else 0.30,
            "summarization": 0.90 if reqs.intent == "summarize" else 0.30
        }
        criticality = "critical" if reqs.security_critical else ("high" if reqs.system_architecture else "medium")

        return self.route_task(
            task_name=reqs.intent,
            task_description=reqs.raw_prompt,
            required_capabilities=task_caps,
            task_complexity=min(workflow_complexity_score, 100.0),
            criticality=criticality,
            context_requirement=reqs.context_requirement
        )

    def _calculate_confidence(self, match_score: float, eligible_count: int, criticality: str) -> float:
        base = match_score
        if eligible_count == 1:
            base += 0.05
        if criticality == "critical":
            base += 0.02
        return round(min(max(base, 0.60), 0.98), 2)
