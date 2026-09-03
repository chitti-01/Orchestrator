import time
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from orchestrator.analysis.analyzer import TaskAnalyzer
from orchestrator.routing.router import ModelRouter
from orchestrator.planning.planner import TaskPlanner
from orchestrator.context.manager import ContextManager
from orchestrator.execution.executor import ModelExecutor
from orchestrator.execution.scheduler import AsyncScheduler
from orchestrator.verification.verifier import Verifier
from orchestrator.recovery.replanner import Replanner
from orchestrator.observability.events import EventTracker

class WorkflowResult(BaseModel):
    workflow_id: str
    status: str
    selected_model: str
    workflow_complexity: float = 0.0
    complexity_score: float = 0.0 # Backwards compatibility alias
    confidence: float
    analysis_confidence: Dict[str, Any] = Field(default_factory=dict)
    task_type: str
    deliverable_type: str = "text"
    scope: str = "single_operation"
    explicit_technologies: List[str] = Field(default_factory=list)
    recommended_technologies: List[str] = Field(default_factory=list)
    explicit_exclusions: List[str] = Field(default_factory=list)
    routing_decision: Dict[str, Any]
    routing_audit: List[Dict[str, Any]] = Field(default_factory=list)
    task_complexities: Dict[str, float] = Field(default_factory=dict)
    task_capabilities: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    plan_nodes: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    verification_passed: bool
    verification_results: Dict[str, Any] = Field(default_factory=dict)
    recovery_trace: List[Dict[str, Any]] = Field(default_factory=list)
    requirement_coverage: List[Dict[str, Any]] = Field(default_factory=list)
    extracted_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    requirement_graph: Dict[str, Any] = Field(default_factory=dict)
    evidence_trails: Dict[str, Any] = Field(default_factory=dict)
    total_latency_ms: float
    estimated_cost: float
    events: List[Dict[str, Any]]

class Orchestrator:
    """
    Public Core Engine Facade for Orchestrator V5 (Production-Grade Per-Task Intelligent Model Orchestrator).
    Enforces Rule 1 (Workflow Complexity != Task Complexity), capability vector matching,
    and genuine heterogeneous model assignments per task.
    """
    def __init__(self, allow_ai_analysis: bool = False, provider=None):
        self.analyzer = TaskAnalyzer(allow_ai_analysis=allow_ai_analysis)
        self.router = ModelRouter()
        self.planner = TaskPlanner(router=self.router)
        self.context_manager = ContextManager()
        self.executor = ModelExecutor(provider=provider)
        self.scheduler = AsyncScheduler(executor=self.executor, context_manager=self.context_manager)
        self.verifier = Verifier()
        self.replanner = Replanner()

    def run_sync(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        return asyncio.run(self.run(prompt, options))

    async def run(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        t0 = time.perf_counter()
        wf_id = f"wf_{uuid.uuid4().hex[:8]}"
        events = EventTracker()

        events.emit("task_received", wf_id, {"prompt": prompt})

        # 1. Fast-Path Requirement Extraction & Requirement Graph & Confidence Evaluation
        events.emit("analysis_started", wf_id, {})
        reqs, req_graph, workflow_complexity, signals, evidence_trails, confidence, analysis_latency, ai_used = self.analyzer.analyze_task(prompt)
        events.emit("analysis_completed", wf_id, {
            "intent": reqs.intent,
            "deliverable": reqs.deliverable_type,
            "scope": reqs.scope,
            "confidence": confidence.overall_confidence,
            "ai_used": ai_used
        })

        # 2. Overall Prompt Routing Decision (for workflow header summary)
        events.emit("routing_started", wf_id, {})
        primary_routing_decision = self.router.route(reqs, workflow_complexity, signals)
        events.emit("routing_decision", wf_id, {"selected_model": primary_routing_decision.selected_model, "tier": primary_routing_decision.tier})

        # 3. Requirement-Driven Workflow Planning & Dynamic DAG Decomposition (Independent Per-Task Routing!)
        events.emit("planning_started", wf_id, {})
        graph, planning_latency = self.planner.plan_workflow(reqs, workflow_complexity, signals, req_graph)
        events.emit("planning_completed", wf_id, {"node_count": len(graph.nodes)})

        # 4. Parallel Execution & Requirement Coverage Verification Loop
        events.emit("execution_started", wf_id, {})
        executed_nodes = await self.scheduler.execute_graph(graph, reqs)
        
        # Requirement Coverage Verification
        v_res = self.verifier.verify_workflow(graph, reqs)
        all_passed = v_res.passed

        # Recovery Loop
        recovery_trace = []
        if not all_passed and options and options.get("allow_replanning", True):
            events.emit("replanning_started", wf_id, {})
            failed_nodes = [n for n in executed_nodes if n.verification_status != "passed"]
            recovery_trace.append({"attempt": 1, "failed_nodes": [f"{n.task_id}: {n.name}" for n in failed_nodes]})
            if self.replanner.replan_failed_nodes(graph, failed_nodes):
                executed_nodes = await self.scheduler.execute_graph(graph, reqs)
                v_res = self.verifier.verify_workflow(graph, reqs)
                all_passed = v_res.passed

        total_latency_ms = (time.perf_counter() - t0) * 1000.0
        events.emit("workflow_completed", wf_id, {"status": "completed", "total_latency_ms": round(total_latency_ms, 2)})

        # Format V5 Structured Audit & Metadata Results
        plan_nodes_output = [node.model_dump() for node in graph.nodes.values()]
        results_output = [{"task_id": n.task_id, "name": n.name, "output": n.result, "status": n.status, "model": n.selected_model} for n in graph.nodes.values()]
        event_logs = [e.model_dump() for e in events.get_events()]
        extracted_reqs_output = [item.model_dump() for item in reqs.extracted_requirements]
        coverage_output = [cov.model_dump() for cov in v_res.coverage]

        # Generate Per-Task Routing Audit & Task Capabilities Maps
        routing_audit = []
        task_complexities = {}
        task_capabilities = {}
        total_est_cost = 0.0

        for n in graph.nodes.values():
            task_complexities[n.task_id] = n.task_complexity
            task_capabilities[n.task_id] = n.required_capabilities
            total_est_cost += n.estimated_cost

            routing_audit.append({
                "task": n.name,
                "task_id": n.task_id,
                "task_complexity": n.task_complexity,
                "criticality": n.criticality,
                "required_capabilities": n.required_capabilities,
                "candidates": {
                    "MODEL_1": {
                        "eligible": "model_1" in n.eligible_models,
                        "rejection_reason": n.rejected_models.get("model_1", ""),
                        "score": n.capability_scores.get("model_1", 0.0)
                    },
                    "MODEL_2": {
                        "eligible": "model_2" in n.eligible_models,
                        "rejection_reason": n.rejected_models.get("model_2", ""),
                        "score": n.capability_scores.get("model_2", 0.0)
                    },
                    "MODEL_3": {
                        "eligible": "model_3" in n.eligible_models,
                        "rejection_reason": n.rejected_models.get("model_3", ""),
                        "score": n.capability_scores.get("model_3", 0.0)
                    }
                },
                "eligible": n.eligible_models,
                "rejected": list(n.rejected_models.keys()),
                "rejection_reasons": n.rejected_models,
                "selected": n.selected_model.upper(),
                "selected_model": n.selected_model,
                "reason": n.selection_reason
            })

        # Primary model is the highest model tier used across tasks or primary decision
        task_models = [n.selected_model for n in graph.nodes.values()]
        primary_model = "model_3" if "model_3" in task_models else ("model_2" if "model_2" in task_models else "model_1")

        return WorkflowResult(
            workflow_id=wf_id,
            status="completed" if all_passed else "completed_with_warnings",
            selected_model=primary_model,
            workflow_complexity=workflow_complexity,
            complexity_score=workflow_complexity,
            confidence=confidence.overall_confidence,
            analysis_confidence=confidence.model_dump(),
            task_type=reqs.intent,
            deliverable_type=reqs.deliverable_type,
            scope=reqs.scope,
            explicit_technologies=reqs.explicit_technologies,
            recommended_technologies=reqs.recommended_technologies,
            explicit_exclusions=reqs.explicit_exclusions,
            routing_decision=primary_routing_decision.model_dump(),
            routing_audit=routing_audit,
            task_complexities=task_complexities,
            task_capabilities=task_capabilities,
            plan_nodes=plan_nodes_output,
            results=results_output,
            verification_passed=all_passed,
            verification_results=v_res.model_dump(),
            recovery_trace=recovery_trace,
            requirement_coverage=coverage_output,
            extracted_requirements=extracted_reqs_output,
            requirement_graph=req_graph.model_dump(),
            evidence_trails=evidence_trails,
            total_latency_ms=round(total_latency_ms, 2),
            estimated_cost=round(total_est_cost or primary_routing_decision.estimated_cost, 4),
            events=event_logs
        )
