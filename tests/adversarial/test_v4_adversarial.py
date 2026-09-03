import pytest
from orchestrator import Orchestrator

@pytest.fixture
def orchestrator():
    return Orchestrator()

def test_v4_critical_case_21_document_platform(orchestrator):
    prompt = (
        "Design and implement a production-grade, multi-tenant AI document-processing platform where users can upload large PDFs concurrently. "
        "The system must extract text and tables, preserve document structure, perform semantic chunking, generate embeddings, support hybrid keyword/vector search, "
        "and provide permission-aware retrieval so one tenant can never access another tenant’s data. It should continue operating during temporary database or object-storage failures, "
        "support horizontal scaling without losing jobs, guarantee that document-processing jobs are not silently lost or duplicated, expose APIs for document upload/search/delete, "
        "provide observability for latency and failed jobs, and include an end-to-end testing strategy. Explain the architecture, identify the major components and their dependencies, "
        "determine which parts can execute independently, and propose how the system should recover when a processing worker crashes halfway through a job. "
        "Do not assume any specific cloud provider, database, message broker, vector database, or programming language unless explicitly justified."
    )
    res = orchestrator.run_sync(prompt)

    assert res.complexity_score >= 70.0
    assert res.selected_model == "model_3"
    assert len(res.plan_nodes) > 1
    assert res.verification_passed is True

    # Rule C Verification: Zero unrequested technologies in outputs or plan
    for node in res.plan_nodes:
        desc_lower = node["description"].lower()
        for unrequested in ["redis", "postgresql", "kafka", "kubernetes", "aws", "azure", "gcp"]:
            assert unrequested not in desc_lower

def test_v4_critical_case_22_short_complex_collab_editor(orchestrator):
    prompt = "Build a globally distributed collaborative editor that guarantees users never observe conflicting document states during concurrent edits and continues accepting writes when an entire region becomes unavailable."
    res = orchestrator.run_sync(prompt)

    assert res.complexity_score >= 68.0
    assert res.selected_model == "model_3"

def test_v4_critical_case_23_simple_tcp_handshake(orchestrator):
    prompt = "Explain the TCP three-way handshake in simple terms."
    res = orchestrator.run_sync(prompt)

    assert res.complexity_score <= 32.0
    assert res.selected_model == "model_1"
    assert len(res.plan_nodes) == 1

def test_v4_critical_case_24_k8s_domain_vs_action(orchestrator):
    res_simple = orchestrator.run_sync("What is Kubernetes?")
    assert res_simple.selected_model == "model_1"
    assert len(res_simple.plan_nodes) == 1

    res_complex = orchestrator.run_sync("Design a multi-region Kubernetes platform that survives complete regional failure while maintaining strict availability and security guarantees.")
    assert res_complex.selected_model == "model_3"
    assert len(res_complex.plan_nodes) > 1

def test_v4_critical_case_25_technology_exclusion(orchestrator):
    prompt = "Design a distributed job processing architecture. Do not assume any specific database, queue, cloud provider, programming language, or framework."
    res = orchestrator.run_sync(prompt)

    assert len(res.explicit_exclusions) > 0
    # Output must not inject unrequested tech
    for node in res.plan_nodes:
        desc = node["description"].lower()
        for forbidden in ["kafka", "redis", "rabbitmq", "postgresql", "aws", "kubernetes", "python", "java"]:
            assert forbidden not in desc
