from typing import Optional
from orchestrator.execution.provider import ModelProvider, ExecutionResult
from orchestrator.execution.mock_provider import MockModelProvider
from orchestrator.context.package import ContextPackage

class ModelExecutor:
    """
    Decoupled Model Executor executing context packages against provider adapters.
    The orchestrator does not directly depend on provider implementations.
    """
    def __init__(self, provider: Optional[ModelProvider] = None):
        self.provider = provider or MockModelProvider()

    async def execute(self, model_id: str, context: ContextPackage) -> ExecutionResult:
        return await self.provider.execute_task(model_id, context)
