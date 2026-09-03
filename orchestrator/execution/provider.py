from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from orchestrator.context.package import ContextPackage

class ExecutionResult:
    def __init__(self, output: str, model_id: str, latency_ms: float, tokens_used: int, success: bool = True, error: Optional[str] = None):
        self.output = output
        self.model_id = model_id
        self.latency_ms = latency_ms
        self.tokens_used = tokens_used
        self.success = success
        self.error = error

class ModelProvider(ABC):
    @abstractmethod
    async def execute_task(self, model_id: str, context: ContextPackage) -> ExecutionResult:
        pass
