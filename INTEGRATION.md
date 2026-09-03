# Enterprise Modular Monolith Integration Guide

The core orchestrator (`orchestrator/`) is designed as a standalone Python package with zero web framework dependencies. It can be directly imported and embedded into any enterprise modular monolith backend.

---

## 1. Import Core Package Direct

```python
from orchestrator import Orchestrator

# Initialize singleton in application context
orchestrator = Orchestrator(allow_ai_analysis=False)

# Run synchronous or asynchronous orchestration
workflow_res = orchestrator.run_sync("Design a distributed payment platform...")

print("Workflow ID:", workflow_res.workflow_id)
print("Primary Selected Model:", workflow_res.selected_model) # "model_3"
print("Complexity Score:", workflow_res.complexity_score)    # 88.0
print("Verification Passed:", workflow_res.verification_passed) # True
```

---

## 2. Register Custom Model Providers

To plug in real model providers (OpenAI, Anthropic, Google, Groq, local vLLM), implement the `ModelProvider` interface:

```python
from orchestrator.execution.provider import ModelProvider, ExecutionResult
from orchestrator.context.package import ContextPackage

class OpenAIModelProvider(ModelProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def execute_task(self, model_id: str, context: ContextPackage) -> ExecutionResult:
        # Call OpenAI API using context.system_prompt and context.task_description
        # Return ExecutionResult(output=..., model_id=model_id, latency_ms=..., tokens_used=...)
        pass

# Inject provider into orchestrator
custom_provider = OpenAIModelProvider(api_key="sk-...")
orchestrator = Orchestrator(provider=custom_provider)
```

---

## 3. Configuration Overrides

Override default policies programmatically or by mounting customized `config/` JSON files:
- `config/models.json`: Register enterprise LLM models and cost profiles.
- `config/routing.json`: Customize capability weights and score thresholds.
- `config/policies.json`: Adjust recovery retries, escalation policies, and concurrency limits.
