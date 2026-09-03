from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from orchestrator.analysis.requirements import TaskRequirements

class AnalysisConfidence(BaseModel):
    overall_confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    requirement_confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    complexity_confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    planning_confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    routing_confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    requires_semantic_analysis: bool = False
    uncertainty_reasons: List[str] = Field(default_factory=list)
    conflicting_signals: List[str] = Field(default_factory=list)

class UncertaintyEvaluator:
    """
    Evaluates analysis confidence and uncertainties based on prompt signals,
    ambiguity, requirement completeness, and conflicting indicators.
    """
    def evaluate(self, reqs: TaskRequirements, complexity_score: float) -> AnalysisConfidence:
        uncertainty_reasons = []
        conflicting_signals = []

        req_conf = 0.92
        comp_conf = 0.92
        plan_conf = 0.90
        rout_conf = 0.90

        # Check Ambiguity & Vague Language
        if reqs.ambiguity >= 0.65:
            req_conf -= 0.20
            uncertainty_reasons.append("High prompt ambiguity or underspecified requirements")

        # Check Conflicting Signals (e.g., Short prompt vs High Actionability)
        words = len(reqs.raw_prompt.split())
        if words <= 10 and reqs.is_actionable and reqs.complexity_score if hasattr(reqs, 'complexity_score') else False:
            conflicting_signals.append("Short prompt length conflicts with high architectural complexity")
            comp_conf -= 0.15

        # Check Requirement Extraction Completeness
        if reqs.is_actionable and len(reqs.extracted_requirements) == 0:
            req_conf -= 0.25
            uncertainty_reasons.append("Actionable request produced zero explicit requirement items")

        # Boundary Proximity Check (near threshold 32.0 or 68.0)
        m1_boundary = abs(complexity_score - 32.0) <= 4.0
        m2_boundary = abs(complexity_score - 68.0) <= 4.0
        if m1_boundary or m2_boundary:
            rout_conf -= 0.15
            uncertainty_reasons.append("Complexity score is within boundary proximity margin of model tier thresholds")

        overall = round(max(0.0, min((req_conf + comp_conf + plan_conf + rout_conf) / 4.0, 1.0)), 2)
        requires_ai = overall < 0.65 or len(conflicting_signals) > 0

        return AnalysisConfidence(
            overall_confidence=overall,
            requirement_confidence=round(max(0.0, min(req_conf, 1.0)), 2),
            complexity_confidence=round(max(0.0, min(comp_conf, 1.0)), 2),
            planning_confidence=round(max(0.0, min(plan_conf, 1.0)), 2),
            routing_confidence=round(max(0.0, min(rout_conf, 1.0)), 2),
            requires_semantic_analysis=requires_ai,
            uncertainty_reasons=uncertainty_reasons,
            conflicting_signals=conflicting_signals
        )
