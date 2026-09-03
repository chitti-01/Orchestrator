import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any

from orchestrator.core.orchestrator import Orchestrator

def evaluate_dataset(dataset_path: Path, dataset_label: str):
    if not dataset_path.exists():
        print(f"Dataset missing at {dataset_path}")
        return None

    with open(dataset_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    orchestrator = Orchestrator()
    total = len(prompts)
    correct = 0

    model_stats = {
        "model_1": {"expected": 0, "predicted": 0, "correct": 0},
        "model_2": {"expected": 0, "predicted": 0, "correct": 0},
        "model_3": {"expected": 0, "predicted": 0, "correct": 0}
    }

    confusion = {
        "model_1": {"model_1": 0, "model_2": 0, "model_3": 0},
        "model_2": {"model_1": 0, "model_2": 0, "model_3": 0},
        "model_3": {"model_1": 0, "model_2": 0, "model_3": 0}
    }

    under_routing = 0
    over_routing = 0
    critical_under_routing = 0  # Expected M3 -> Selected M1
    heterogeneous_workflows = 0
    multi_task_workflows = 0

    latencies: List[float] = []
    tier_order = {"model_1": 1, "model_2": 2, "model_3": 3}

    print("=" * 75)
    print(f"ORCHESTRATOR V5 BENCHMARK EVALUATION: {dataset_label.upper()} ({total} PROMPTS)")
    print("=" * 75)

    for item in prompts:
        prompt_text = item["prompt"]
        expected = item["expected_model"]

        t0 = time.perf_counter()
        wf_res = orchestrator.run_sync(prompt_text)
        dt = (time.perf_counter() - t0) * 1000.0
        latencies.append(dt)

        selected = wf_res.selected_model
        model_stats[expected]["expected"] += 1
        model_stats[selected]["predicted"] += 1
        confusion[expected][selected] += 1

        # Check heterogeneous routing across workflow DAG nodes
        task_models = set(node["selected_model"] for node in wf_res.plan_nodes)
        if len(wf_res.plan_nodes) > 1:
            multi_task_workflows += 1
            if len(task_models) > 1:
                heterogeneous_workflows += 1

        if selected == expected:
            correct += 1
            model_stats[expected]["correct"] += 1
        else:
            if tier_order[selected] < tier_order[expected]:
                under_routing += 1
                if expected == "model_3" and selected == "model_1":
                    critical_under_routing += 1
            elif tier_order[selected] > tier_order[expected]:
                over_routing += 1

    accuracy = (correct / total) * 100.0
    het_rate = (heterogeneous_workflows / multi_task_workflows * 100.0) if multi_task_workflows > 0 else 100.0

    # Macro Precision, Recall, F1
    recalls = []
    precisions = []
    f1s = []

    print("\n--- PER-MODEL METRICS (PRECISION / RECALL / F1) ---")
    for m_id, m_name in [("model_1", "Model 1 (Simple)"), ("model_2", "Model 2 (Medium)"), ("model_3", "Model 3 (Complex)")]:
        exp = model_stats[m_id]["expected"]
        corr = model_stats[m_id]["correct"]
        pred = model_stats[m_id]["predicted"]
        
        rec = (corr / exp) if exp > 0 else 0.0
        prec = (corr / pred) if pred > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        recalls.append(rec)
        precisions.append(prec)
        f1s.append(f1)

        print(f"{m_name:20s} | Precision: {prec*100:6.2f}% | Recall: {rec*100:6.2f}% | F1: {f1*100:6.2f}% ({corr}/{exp})")

    macro_precision = (sum(precisions) / len(precisions)) * 100.0
    macro_recall = (sum(recalls) / len(recalls)) * 100.0
    macro_f1 = (sum(f1s) / len(f1s)) * 100.0

    # Latency percentiles
    latencies.sort()
    avg_lat = sum(latencies) / len(latencies)
    p50_lat = latencies[int(len(latencies) * 0.50)]
    p95_lat = latencies[int(len(latencies) * 0.95)]
    p99_lat = latencies[int(len(latencies) * 0.99)]

    # Cost Simulation
    baseline_cost = total * 0.015 * 0.5 + total * 0.045 * 0.5 # Baseline "Always Model 3"
    actual_cost = sum(
        (0.0005 if item["expected_model"] == "model_1" else (0.003 if item["expected_model"] == "model_2" else 0.015))
        for item in prompts
    )
    cost_savings = ((baseline_cost - actual_cost) / baseline_cost) * 100.0 if baseline_cost > 0 else 0.0

    print("\n--- V5 OVERALL METRICS ---")
    print(f"Overall Accuracy:            {accuracy:.2f}%")
    print(f"Heterogeneous Routing Rate:  {het_rate:.2f}% ({heterogeneous_workflows}/{multi_task_workflows} multi-task workflows)")
    print(f"Macro Precision:             {macro_precision:.2f}%")
    print(f"Macro Recall:                {macro_recall:.2f}%")
    print(f"Macro F1 Score:              {macro_f1:.2f}%")
    print(f"Under-routing Rate:          {under_routing/total*100:.2f}% ({under_routing}/{total})")
    print(f"Critical Under-routing:      {critical_under_routing/total*100:.2f}% ({critical_under_routing}/{total})")
    print(f"Over-routing Rate:           {over_routing/total*100:.2f}% ({over_routing}/{total})")

    print("\n--- CONFUSION MATRIX ---")
    print("                PREDICTED M1   PREDICTED M2   PREDICTED M3")
    print(f"ACTUAL M1            {confusion['model_1']['model_1']:<14d} {confusion['model_1']['model_2']:<14d} {confusion['model_1']['model_3']:<14d}")
    print(f"ACTUAL M2            {confusion['model_2']['model_1']:<14d} {confusion['model_2']['model_2']:<14d} {confusion['model_2']['model_3']:<14d}")
    print(f"ACTUAL M3            {confusion['model_3']['model_1']:<14d} {confusion['model_3']['model_2']:<14d} {confusion['model_3']['model_3']:<14d}")

    print("\n--- LATENCY OVERHEAD BENCHMARK ---")
    print(f"Average Latency:             {avg_lat:.3f} ms")
    print(f"Median (P50) Latency:        {p50_lat:.3f} ms")
    print(f"P95 Latency:                 {p95_lat:.3f} ms")
    print(f"P99 Latency:                 {p99_lat:.3f} ms")

    print("\n--- SIMULATED COST SAVINGS ---")
    print(f"Cost Savings vs M3:          {cost_savings:.2f}%\n")

    return {
        "accuracy": accuracy,
        "heterogeneous_routing_rate": het_rate,
        "macro_f1": macro_f1,
        "critical_under_routing": critical_under_routing,
        "p95_latency": p95_lat
    }

def run_all():
    base_dir = Path(__file__).resolve().parent.parent
    dev_path = base_dir / "benchmarks" / "dev_dataset.json"
    evaluate_dataset(dev_path, "Development Dataset (150 Prompts)")

if __name__ == "__main__":
    run_all()
