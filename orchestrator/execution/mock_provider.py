import asyncio
import time
from typing import Dict, Any, Optional
from orchestrator.execution.provider import ModelProvider, ExecutionResult
from orchestrator.context.package import ContextPackage

class MockModelProvider(ModelProvider):
    """
    Mock Provider enabling zero-API-key development, execution, and benchmarking.
    Simulates latency, context packaging, token counts, and realistic task completion.
    ENFORCES RULE C: Zero Technology Hallucination (Does NOT inject Redis/Kafka/PostgreSQL/Kubernetes).
    """
    def __init__(self, simulate_latency: bool = True, failure_trigger_name: Optional[str] = None):
        self.simulate_latency = simulate_latency
        self.failure_trigger_name = failure_trigger_name

    async def execute_task(self, model_id: str, context: ContextPackage) -> ExecutionResult:
        t0 = time.perf_counter()

        # Latency simulation per tier
        if self.simulate_latency:
            delay_ms = 10 if model_id == "model_1" else (25 if model_id == "model_2" else 50)
            await asyncio.sleep(delay_ms / 1000.0)

        # Failure trigger simulation
        if self.failure_trigger_name and self.failure_trigger_name in context.task_name:
            elapsed = (time.perf_counter() - t0) * 1000.0
            return ExecutionResult(
                output="",
                model_id=model_id,
                latency_ms=round(elapsed, 2),
                tokens_used=100,
                success=False,
                error=f"Simulated execution failure in node {context.task_name}"
            )

        # Generate realistic output artifact reflecting exact task description
        output_content = self._generate_mock_output(context, model_id)
        tokens = int(len(context.task_description.split()) * 1.5) + int(len(output_content.split()) * 1.3)
        elapsed = (time.perf_counter() - t0) * 1000.0

        return ExecutionResult(
            output=output_content,
            model_id=model_id,
            latency_ms=round(elapsed, 2),
            tokens_used=tokens,
            success=True
        )

    def _generate_mock_output(self, context: ContextPackage, model_id: str) -> str:
        name = context.task_name
        desc = context.task_description
        model_label = model_id.upper()

        if "Reverse" in desc:
            return f"def reverse_string(s: str) -> str:\n    return s[::-1]\n# Executed via {model_label}"

        if "Fermat" in desc:
            return f"[{model_label} Formal Proof]: By Andrew Wiles (1995) using modular elliptic curves, a^n + b^n = c^n has no non-zero integer solutions for n > 2. Verified PASS."

        # Clean generic mock output deriving response from task description without technology hallucination
        return f"[{model_label} MOCK EXECUTION]\nCompleted task: '{name}'\nRequirement addressed: {desc}\nNo unrequested technologies selected."
