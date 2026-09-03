import pytest
from orchestrator.core.orchestrator import Orchestrator

@pytest.fixture
def orchestrator():
    return Orchestrator()

def test_payment_domain_vs_action(orchestrator):
    # Domain Q&A -> Model 1
    res_simple = orchestrator.run_sync("What is a payment gateway?")
    assert res_simple.selected_model == "model_1"
    assert res_simple.complexity_score <= 32.0

    # Build simple gateway -> Model 2
    res_medium = orchestrator.run_sync("Build a payment gateway.")
    assert res_medium.selected_model == "model_2"

    # Build production platform -> Model 3
    res_complex = orchestrator.run_sync("Build a production payment platform with authentication, transaction processing, fraud detection, database replication, fault tolerance and PCI compliance.")
    assert res_complex.selected_model == "model_3"
    assert res_complex.complexity_score >= 68.0

def test_kubernetes_domain_vs_action(orchestrator):
    res_simple = orchestrator.run_sync("What is Kubernetes?")
    assert res_simple.selected_model == "model_1"

    res_complex = orchestrator.run_sync("Design a multi-region Kubernetes platform.")
    assert res_complex.selected_model == "model_3"

def test_os_domain_vs_action(orchestrator):
    res_simple = orchestrator.run_sync("Explain operating systems.")
    assert res_simple.selected_model == "model_1"

    res_complex = orchestrator.run_sync("Build an operating system.")
    assert res_complex.selected_model == "model_3"

def test_math_fermat_proof(orchestrator):
    res = orchestrator.run_sync("Prove Fermat's Last Theorem.")
    assert res.selected_model == "model_3"
