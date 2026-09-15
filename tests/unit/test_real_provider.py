import os
import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from orchestrator.execution.provider import ExecutionResult
from orchestrator.execution.real_provider import RealModelProvider
from orchestrator.execution.executor import ModelExecutor
from orchestrator.execution.mock_provider import MockModelProvider
from orchestrator.context.package import ContextPackage
from orchestrator.models.registry import ModelRegistry

@pytest.fixture
def sample_context():
    return ContextPackage(
        task_id="task_test_01",
        task_name="Write Python Function",
        task_description="Write a python function to add two numbers.",
        global_objective="Write a python function to add two numbers.",
        system_prompt="You are a helpful coding assistant.",
        parent_results={}
    )


@pytest.mark.asyncio
async def test_real_provider_missing_api_key(sample_context, monkeypatch):
    # Ensure no API keys exist in env
    monkeypatch.delenv("MODEL_1_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    provider = RealModelProvider()
    res = await provider.execute_task("model_1", sample_context)

    assert res.success is False
    assert "AuthenticationError" in res.error
    assert "MODEL_1_API_KEY" in res.error
    assert res.provider == "openai"
    assert res.actual_model_name == "gpt-4o-mini"

@pytest.mark.asyncio
async def test_real_provider_successful_openai_call(sample_context, monkeypatch):
    monkeypatch.setenv("MODEL_1_API_KEY", "sk-mock-key-12345")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": "def add(a, b):\n    return a + b"}}
        ],
        "usage": {"total_tokens": 42}
    }
    mock_response.raise_for_status = MagicMock()

    mock_post = AsyncMock(return_value=mock_response)

    with patch.object(httpx.AsyncClient, "post", mock_post):
        provider = RealModelProvider()
        res = await provider.execute_task("model_1", sample_context)

        assert res.success is True
        assert "def add(a, b):" in res.output
        assert res.tokens_used == 42
        assert res.provider == "openai"
        assert res.actual_model_name == "gpt-4o-mini"
        assert res.error is None

@pytest.mark.asyncio
async def test_real_provider_timeout_handling(sample_context, monkeypatch):
    monkeypatch.setenv("MODEL_1_API_KEY", "sk-mock-key-12345")

    with patch.object(httpx.AsyncClient, "post", side_effect=httpx.TimeoutException("Connection timed out")):
        provider = RealModelProvider()
        res = await provider.execute_task("model_1", sample_context)

        assert res.success is False
        assert "TimeoutError" in res.error
        assert res.provider == "openai"

@pytest.mark.asyncio
async def test_real_provider_http_error_handling(sample_context, monkeypatch):
    monkeypatch.setenv("MODEL_1_API_KEY", "sk-invalid-key")

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Incorrect API key provided"
    
    http_err = httpx.HTTPStatusError("401 Unauthorized", request=MagicMock(), response=mock_resp)

    with patch.object(httpx.AsyncClient, "post", side_effect=http_err):
        provider = RealModelProvider()
        res = await provider.execute_task("model_1", sample_context)

        assert res.success is False
        assert "ProviderAPIError [401]" in res.error
        assert "Incorrect API key" in res.error

def test_executor_provider_selection(monkeypatch):
    # Production default should select RealModelProvider
    monkeypatch.delenv("USE_MOCK_PROVIDER", raising=False)
    monkeypatch.delenv("ORCHESTRATOR_ENV", raising=False)
    exec_prod = ModelExecutor()
    assert isinstance(exec_prod.provider, RealModelProvider)

    # Explicit mock flag should select MockModelProvider
    monkeypatch.setenv("USE_MOCK_PROVIDER", "true")
    exec_mock = ModelExecutor()
    assert isinstance(exec_mock.provider, MockModelProvider)

    # Explicit provider instance override
    custom_mock = MockModelProvider()
    exec_custom = ModelExecutor(provider=custom_mock)
    assert exec_custom.provider is custom_mock
