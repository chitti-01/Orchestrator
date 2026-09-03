import pytest
from orchestrator.analysis.deterministic_analyzer import DeterministicAnalyzer
from orchestrator.analysis.complexity import ComplexityAnalyzer

@pytest.fixture
def analyzer():
    return DeterministicAnalyzer()

@pytest.fixture
def complexity():
    return ComplexityAnalyzer()

def test_feature_interactions(analyzer, complexity):
    reqs = analyzer.analyze("Build a production payment platform with authentication, transaction processing, fraud detection, database replication, fault tolerance and PCI compliance.")
    score, signals = complexity.compute_complexity(reqs)
    
    assert score >= 70.0
    assert any("Feature Interaction" in s for s in signals)

def test_informational_query_cap(analyzer, complexity):
    reqs = analyzer.analyze("Explain operating systems.")
    score, signals = complexity.compute_complexity(reqs)
    
    assert score <= 32.0
    assert any("Informational Query" in s for s in signals)
