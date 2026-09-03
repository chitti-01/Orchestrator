from fastapi import APIRouter, HTTPException, status
from api.schemas.request import OrchestrationAPIRequest
from api.schemas.response import OrchestrationAPIResponse, OrchestrationMetrics
from orchestrator import Orchestrator

router = APIRouter(prefix="/api", tags=["orchestration"])

orchestrator_instance = Orchestrator()

@router.post("/orchestrate", response_model=OrchestrationAPIResponse)
async def orchestrate_request(payload: OrchestrationAPIRequest):
    try:
        opts = payload.options.model_dump() if payload.options else {}
        res = await orchestrator_instance.run(payload.prompt, opts)
        
        return OrchestrationAPIResponse(
            workflow_id=res.workflow_id,
            status=res.status,
            selected_model=res.selected_model,
            workflow_complexity=res.workflow_complexity,
            complexity_score=res.complexity_score,
            confidence=res.confidence,
            analysis_confidence=res.analysis_confidence,
            task_type=res.task_type,
            deliverable_type=res.deliverable_type,
            scope=res.scope,
            explicit_technologies=res.explicit_technologies,
            recommended_technologies=res.recommended_technologies,
            explicit_exclusions=res.explicit_exclusions,
            routing_decision=res.routing_decision,
            routing_audit=res.routing_audit,
            task_complexities=res.task_complexities,
            task_capabilities=res.task_capabilities,
            plan=res.plan_nodes,
            results=res.results,
            verification_passed=res.verification_passed,
            verification_results=res.verification_results,
            recovery_trace=res.recovery_trace,
            requirement_coverage=res.requirement_coverage,
            extracted_requirements=res.extracted_requirements,
            requirement_graph=res.requirement_graph,
            evidence_trails=res.evidence_trails,
            metrics=OrchestrationMetrics(
                total_latency_ms=res.total_latency_ms,
                estimated_cost=res.estimated_cost
            ),
            events=res.events
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration engine failure: {str(e)}"
        )

@router.get("/models")
async def list_registered_models():
    models = orchestrator_instance.router.registry.list_models()
    return {k: v.model_dump() for k, v in models.items()}
