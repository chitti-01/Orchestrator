import os
import time
import asyncio
import httpx
from typing import Dict, Any, Optional
from orchestrator.execution.provider import ModelProvider, ExecutionResult
from orchestrator.context.package import ContextPackage
from orchestrator.models.registry import ModelRegistry
from orchestrator.execution.mock_provider import MockModelProvider

class RealModelProvider(ModelProvider):
    """
    Production-grade Real Model Provider executing context packages against 
    external LLM APIs (OpenAI, Anthropic, Google Gemini, Groq, OpenRouter, Ollama)
    via standard, asynchronous HTTP protocol endpoints.
    Reads API credentials securely from backend environment variables.
    """
    def __init__(self, registry: Optional[ModelRegistry] = None, timeout_seconds: float = 30.0):
        self.registry = registry or ModelRegistry()
        self.timeout_seconds = timeout_seconds
        self.mock_fallback_provider = MockModelProvider()

    async def execute_task(self, model_id: str, context: ContextPackage) -> ExecutionResult:
        t0 = time.perf_counter()
        model_profile = self.registry.get_model(model_id)

        if not model_profile:
            elapsed = (time.perf_counter() - t0) * 1000.0
            return ExecutionResult(
                output="",
                model_id=model_id,
                latency_ms=round(elapsed, 2),
                tokens_used=0,
                success=False,
                error=f"ModelNotFoundError: Model '{model_id}' is not registered in ModelRegistry."
            )

        provider_type = (model_profile.provider or "openai").lower()
        model_name = model_profile.model_name or model_id

        # If model profile is explicitly configured as mock (e.g. for offline benchmarking)
        if provider_type == "mock":
            return await self.mock_fallback_provider.execute_task(model_id, context)

        # Resolve API Key securely from environment variables
        api_key = self._resolve_api_key(model_profile, provider_type)

        # Enforce API Key requirement (except local providers like Ollama)
        if not api_key and provider_type not in ["ollama", "local"]:
            elapsed = (time.perf_counter() - t0) * 1000.0
            req_env = model_profile.api_key_env or f"{provider_type.upper()}_API_KEY"
            return ExecutionResult(
                output="",
                model_id=model_id,
                latency_ms=round(elapsed, 2),
                tokens_used=0,
                success=False,
                error=f"AuthenticationError: Missing API key for model '{model_id}' ({provider_type}). Please set environment variable {req_env}.",
                provider=provider_type,
                actual_model_name=model_name
            )

        api_base = self._resolve_api_base(model_profile, provider_type)

        # Dispatch API request to appropriate provider protocol handler
        try:
            if provider_type in ["openai", "groq", "openrouter", "ollama", "vllm", "deepseek"]:
                res = await self._call_openai_compatible_api(provider_type, model_name, api_key, api_base, context)
            elif provider_type == "anthropic":
                res = await self._call_anthropic_api(model_name, api_key, api_base, context)
            elif provider_type in ["google", "gemini"]:
                res = await self._call_gemini_api(model_name, api_key, context)
            else:
                # Fallback to OpenAI compatible protocol for custom HTTP endpoints
                res = await self._call_openai_compatible_api(provider_type, model_name, api_key, api_base, context)

            elapsed = (time.perf_counter() - t0) * 1000.0
            return ExecutionResult(
                output=res["output"],
                model_id=model_id,
                latency_ms=round(elapsed, 2),
                tokens_used=res.get("tokens_used", 0),
                success=True,
                provider=provider_type,
                actual_model_name=model_name
            )

        except httpx.TimeoutException:
            elapsed = (time.perf_counter() - t0) * 1000.0
            return ExecutionResult(
                output="",
                model_id=model_id,
                latency_ms=round(elapsed, 2),
                tokens_used=0,
                success=False,
                error=f"TimeoutError: HTTP request to provider '{provider_type}' for model '{model_name}' timed out after {self.timeout_seconds}s.",
                provider=provider_type,
                actual_model_name=model_name
            )
        except httpx.HTTPStatusError as e:
            elapsed = (time.perf_counter() - t0) * 1000.0
            status_code = e.response.status_code
            error_body = e.response.text
            return ExecutionResult(
                output="",
                model_id=model_id,
                latency_ms=round(elapsed, 2),
                tokens_used=0,
                success=False,
                error=f"ProviderAPIError [{status_code}] ({provider_type}): {error_body[:300]}",
                provider=provider_type,
                actual_model_name=model_name
            )
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000.0
            return ExecutionResult(
                output="",
                model_id=model_id,
                latency_ms=round(elapsed, 2),
                tokens_used=0,
                success=False,
                error=f"ProviderExecutionError ({provider_type}): {str(e)}",
                provider=provider_type,
                actual_model_name=model_name
            )

    def _resolve_api_key(self, model_profile, provider_type: str) -> Optional[str]:
        # 1. Configured specific model env key
        if model_profile.api_key_env and os.getenv(model_profile.api_key_env):
            return os.getenv(model_profile.api_key_env)
        # 2. Provider-specific standard env key
        provider_env = f"{provider_type.upper()}_API_KEY"
        if os.getenv(provider_env):
            return os.getenv(provider_env)
        # 3. Global fallback LLM key
        return os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")

    def _resolve_api_base(self, model_profile, provider_type: str) -> str:
        if model_profile.api_base_env and os.getenv(model_profile.api_base_env):
            return os.getenv(model_profile.api_base_env)
        if model_profile.api_base:
            return model_profile.api_base

        defaults = {
            "openai": "https://api.openai.com/v1",
            "groq": "https://api.groq.com/openai/v1",
            "openrouter": "https://openrouter.ai/api/v1",
            "ollama": "http://localhost:11434/v1",
            "anthropic": "https://api.anthropic.com/v1",
            "google": "https://generativelanguage.googleapis.com/v1beta"
        }
        return defaults.get(provider_type, "https://api.openai.com/v1")

    async def _call_openai_compatible_api(self, provider_type: str, model_name: str, api_key: str, api_base: str, context: ContextPackage) -> Dict[str, Any]:
        url = f"{api_base.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        messages = []
        if context.system_prompt:
            messages.append({"role": "system", "content": context.system_prompt})

        user_content = f"Task: {context.task_name}\nDescription: {context.task_description}"
        parent_res = getattr(context, "parent_results", None) or getattr(context, "parent_outputs", {})
        if parent_res:
            user_content += "\n\nContext Inputs from parent dependencies:\n"
            for p_id, p_out in parent_res.items():
                user_content += f"- Output from {p_id}:\n{p_out}\n"


        messages.append({"role": "user", "content": user_content})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

            output_text = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            return {"output": output_text, "tokens_used": tokens_used}

    async def _call_anthropic_api(self, model_name: str, api_key: str, api_base: str, context: ContextPackage) -> Dict[str, Any]:
        url = f"{api_base.rstrip('/')}/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }

        user_content = f"Task: {context.task_name}\nDescription: {context.task_description}"
        parent_res = getattr(context, "parent_results", None) or getattr(context, "parent_outputs", {})
        if parent_res:
            user_content += "\n\nContext Inputs from parent dependencies:\n"
            for p_id, p_out in parent_res.items():
                user_content += f"- Output from {p_id}:\n{p_out}\n"


        payload = {
            "model": model_name,
            "system": context.system_prompt or "You are a specialized AI execution agent.",
            "messages": [{"role": "user", "content": user_content}],
            "max_tokens": 4096
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

            output_text = data["content"][0]["text"]
            usage = data.get("usage", {})
            tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            return {"output": output_text, "tokens_used": tokens_used}

    async def _call_gemini_api(self, model_name: str, api_key: str, context: ContextPackage) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}

        user_content = f"Task: {context.task_name}\nDescription: {context.task_description}"
        parent_res = getattr(context, "parent_results", None) or getattr(context, "parent_outputs", {})
        if parent_res:
            user_content += "\n\nContext Inputs from parent dependencies:\n"
            for p_id, p_out in parent_res.items():
                user_content += f"- Output from {p_id}:\n{p_out}\n"


        payload = {
            "contents": [{"parts": [{"text": user_content}]}],
            "systemInstruction": {"parts": [{"text": context.system_prompt or "You are an AI execution agent."}]}
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

            output_text = data["candidates"][0]["content"]["parts"][0]["text"]
            tokens_used = data.get("usageMetadata", {}).get("totalTokenCount", 0)
            return {"output": output_text, "tokens_used": tokens_used}
