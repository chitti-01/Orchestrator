import os
from typing import Optional
from orchestrator.execution.provider import ModelProvider, ExecutionResult
from orchestrator.execution.mock_provider import MockModelProvider
from orchestrator.execution.real_provider import RealModelProvider
from orchestrator.context.package import ContextPackage

class ModelExecutor:
    """
    Decoupled Model Executor executing context packages against provider adapters.
    Evaluates provider dynamically per execution call, defaulting to RealModelProvider
    for production execution, or MockModelProvider when explicitly passed or when 
    USE_MOCK_PROVIDER=true / ORCHESTRATOR_ENV=test is set.
    """
    def __init__(self, provider: Optional[ModelProvider] = None):
        self._custom_provider = provider
        self._real_provider_instance: Optional[RealModelProvider] = None
        self._mock_provider_instance: Optional[MockModelProvider] = None

    @property
    def provider(self) -> ModelProvider:
        if self._custom_provider is not None:
            return self._custom_provider
        if os.getenv("USE_MOCK_PROVIDER", "").lower() in ["true", "1", "yes"] or os.getenv("ORCHESTRATOR_ENV") == "test":
            if self._mock_provider_instance is None:
                self._mock_provider_instance = MockModelProvider()
            return self._mock_provider_instance
        else:
            if self._real_provider_instance is None:
                self._real_provider_instance = RealModelProvider()
            return self._real_provider_instance

    async def execute(self, model_id: str, context: ContextPackage) -> ExecutionResult:
        return await self.provider.execute_task(model_id, context)


