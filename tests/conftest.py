import os
import pytest

@pytest.fixture(autouse=True)
def set_testing_environment(monkeypatch):
    """
    Automatically ensures pytest runs in offline mock provider mode by default,
    preventing unit tests from attempting live network calls to external APIs.
    """
    monkeypatch.setenv("USE_MOCK_PROVIDER", "true")
    monkeypatch.setenv("ORCHESTRATOR_ENV", "test")
