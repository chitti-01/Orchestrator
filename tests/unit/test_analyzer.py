import pytest
from orchestrator.analysis.deterministic_analyzer import DeterministicAnalyzer

@pytest.fixture
def analyzer():
    return DeterministicAnalyzer()

def test_explain_vs_build(analyzer):
    req_explain = analyzer.analyze("What is a payment gateway?")
    assert req_explain.intent == "explain"
    assert req_explain.is_actionable is False

    req_build = analyzer.analyze("Build a payment gateway.")
    assert req_build.intent == "build"
    assert req_build.is_actionable is True

def test_formal_proof_extraction(analyzer):
    req_proof = analyzer.analyze("Prove Fermat's Last Theorem.")
    assert req_proof.intent == "prove"
    assert req_proof.formal_proof is True
    assert req_proof.reasoning_depth >= 0.90
