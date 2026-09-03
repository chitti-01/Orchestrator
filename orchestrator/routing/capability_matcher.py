from typing import Dict, Tuple, List, Any, Optional
from orchestrator.models.profile import ModelCapabilityProfile
from orchestrator.models.registry import ModelRegistry
from orchestrator.policy.engine import PolicyEngine

class CapabilityMatchResult:
    def __init__(
        self,
        scores: Dict[str, float],
        eligible_models: List[str],
        rejected_models: Dict[str, str],
        gaps: Dict[str, List[Dict[str, Any]]],
        model_caps: Dict[str, Dict[str, float]]
    ):
        self.scores = scores
        self.eligible_models = eligible_models
        self.rejected_models = rejected_models
        self.gaps = gaps
        self.model_caps = model_caps

class CapabilityMatcher:
    """
    V5 Fine-Grained Capability Vector Matching Engine.
    Calculates capability_gap(model, task) for every required capability dimension.
    Enforces critical capability floors and eligibility filtering before model selection.
    """
    def __init__(self, registry: ModelRegistry, policy_engine: Optional[PolicyEngine] = None):
        self.registry = registry
        self.policy_engine = policy_engine or PolicyEngine()

    def evaluate_task(
        self,
        required_capabilities: Dict[str, float],
        criticality: str = "medium",
        context_requirement: float = 0.05
    ) -> CapabilityMatchResult:
        models = self.registry.list_models()
        thresholds = self.policy_engine.get_thresholds()
        
        critical_gap_limit = thresholds.get("critical_gap_threshold", 0.15)
        max_avg_gap = thresholds.get("max_average_gap", 0.25)

        scores: Dict[str, float] = {}
        eligible_models: List[str] = []
        rejected_models: Dict[str, str] = {}
        gaps_by_model: Dict[str, List[Dict[str, Any]]] = {}
        model_caps_dict: Dict[str, Dict[str, float]] = {}

        if not required_capabilities:
            required_capabilities = {"reasoning": 0.30, "implementation": 0.30}

        for m_id, profile in models.items():
            caps = profile.capabilities
            caps_dict = caps.model_dump() if hasattr(caps, "model_dump") else caps.__dict__
            model_caps_dict[m_id] = {k: float(v) for k, v in caps_dict.items() if isinstance(v, (int, float))}

            model_gaps: List[Dict[str, Any]] = []
            max_single_gap = 0.0
            total_gap = 0.0
            rejection_reasons: List[str] = []

            for cap_name, req_val in required_capabilities.items():
                if req_val <= 0.0:
                    continue
                provided_val = float(caps_dict.get(cap_name, 0.40))
                gap = max(0.0, req_val - provided_val)
                gap_obj = {
                    "capability": cap_name,
                    "required": round(req_val, 2),
                    "provided": round(provided_val, 2),
                    "gap": round(gap, 2)
                }
                model_gaps.append(gap_obj)

                if gap > max_single_gap:
                    max_single_gap = gap
                total_gap += gap

                # Critical floor check: strict gap limit when requirement is high/critical
                if req_val >= 0.75 or criticality in ["high", "critical"]:
                    if gap > critical_gap_limit:
                        rejection_reasons.append(
                            f"insufficient {cap_name} capability (required: {req_val:.2f}, provided: {provided_val:.2f}, gap: {gap:.2f})"
                        )
                elif gap >= 0.35:
                    rejection_reasons.append(
                        f"large capability gap in {cap_name} (required: {req_val:.2f}, provided: {provided_val:.2f}, gap: {gap:.2f})"
                    )

            avg_gap = total_gap / len(model_gaps) if model_gaps else 0.0

            # Context capacity check
            req_context_tokens = int(context_requirement * 150000)
            if profile.capabilities.context_window < req_context_tokens and req_context_tokens > 16000:
                rejection_reasons.append(
                    f"context requirement {req_context_tokens} tokens exceeds capacity {profile.capabilities.context_window}"
                )

            # Overall average gap check for high/critical tasks
            if avg_gap > max_avg_gap and criticality in ["high", "critical"]:
                if not rejection_reasons:
                    rejection_reasons.append(f"average capability gap {avg_gap:.2f} exceeds threshold {max_avg_gap:.2f}")

            gaps_by_model[m_id] = model_gaps
            match_score = max(0.0, min(1.0, 1.0 - avg_gap))
            scores[m_id] = round(match_score, 3)

            if rejection_reasons:
                rejected_models[m_id] = "; ".join(rejection_reasons)
            else:
                eligible_models.append(m_id)

        # Fallback safety: if all models rejected due to strict thresholds, make highest capability model eligible
        if not eligible_models:
            best_m = max(scores.keys(), key=lambda k: scores[k])
            eligible_models.append(best_m)
            if best_m in rejected_models:
                del rejected_models[best_m]

        return CapabilityMatchResult(
            scores=scores,
            eligible_models=eligible_models,
            rejected_models=rejected_models,
            gaps=gaps_by_model,
            model_caps=model_caps_dict
        )
