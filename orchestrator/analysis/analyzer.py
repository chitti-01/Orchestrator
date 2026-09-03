import time
from typing import Tuple, List, Dict, Optional
from orchestrator.analysis.requirements import TaskRequirements
from orchestrator.analysis.requirement_analyzer import RequirementAnalyzer
from orchestrator.analysis.requirement_graph import RequirementGraph
from orchestrator.analysis.confidence import UncertaintyEvaluator, AnalysisConfidence
from orchestrator.analysis.complexity import ComplexityAnalyzer
from orchestrator.analysis.semantic_analyzer import SemanticAIAnalyzer

class TaskAnalyzer:
    """
    V4 Task Analyzer Facade coordinating Layer 1 Fast Path Engine, Uncertainty Evaluation,
    and optional Layer 2 Semantic AI Fallback.
    """
    def __init__(self, allow_ai_analysis: bool = False):
        self.req_analyzer = RequirementAnalyzer()
        self.complexity_engine = ComplexityAnalyzer()
        self.uncertainty_evaluator = UncertaintyEvaluator()
        self.semantic_engine = SemanticAIAnalyzer(enabled=allow_ai_analysis)

    def analyze_task(self, prompt: str) -> Tuple[TaskRequirements, RequirementGraph, float, List[str], Dict, AnalysisConfidence, float, bool]:
        t0 = time.perf_counter()

        # Step 1: Requirement Extraction & Requirement Graph Construction
        reqs, req_graph = self.req_analyzer.extract_requirements(prompt)

        # Step 2: Multi-dimensional Complexity & Evidence Trails
        complexity_score, signals, evidence_trails = self.complexity_engine.compute_complexity_with_evidence(reqs)

        # Step 3: Explicit Uncertainty & Confidence Evaluation
        confidence = self.uncertainty_evaluator.evaluate(reqs, complexity_score)

        # Step 4: Optional Layer 2 AI Semantic Fallback when confidence is low
        ai_used = False
        if confidence.requires_semantic_analysis and self.semantic_engine.enabled:
            reqs = self.semantic_engine.analyze(prompt, reqs)
            ai_used = True

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return reqs, req_graph, complexity_score, signals, evidence_trails, confidence, round(latency_ms, 3), ai_used
