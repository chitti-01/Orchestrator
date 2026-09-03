import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_api_orchestrate_simple():
    res = client.post("/api/orchestrate", json={"prompt": "Reverse a string in Python."})
    assert res.status_code == 200
    data = res.json()
    assert data["selected_model"] == "model_1"
    assert data["status"] == "completed"
    assert data["verification_passed"] is True
    assert data["metrics"]["total_latency_ms"] >= 0.0

def test_api_orchestrate_complex():
    res = client.post("/api/orchestrate", json={"prompt": "Build a production payment platform with authentication, transaction processing, fraud detection, database replication, fault tolerance and PCI compliance."})
    assert res.status_code == 200
    data = res.json()
    assert data["selected_model"] == "model_3"
    assert len(data["plan"]) > 1
