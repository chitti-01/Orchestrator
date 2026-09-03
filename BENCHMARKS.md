# V4 Benchmark Suite & Quality Metrics

The engine includes a **300-Prompt Benchmark Suite** split into 150 Development prompts (`benchmarks/dev_dataset.json`) and 150 Unseen Evaluation prompts (`benchmarks/eval_dataset.json`).

---

## 1. Measured V4 Performance Summary

| Metric | Measured Benchmark Result |
| :--- | :--- |
| **Total Benchmark Prompts** | 150 Prompts (Dev Dataset) |
| **Overall Accuracy** | **80.67%** |
| **Macro Precision** | **81.28%** |
| **Macro Recall** | **80.84%** |
| **Macro F1 Score** | **80.66%** |
| **Model 3 (Complex) Precision** | **93.48%** (43 / 54 recall) |
| **Model 2 (Medium) Precision** | **80.00%** (40 / 51 recall) |
| **Model 1 (Simple) Recall** | **84.44%** (38 / 45 correct) |
| **Under-Routing Rate** | **13.33%** |
| **Critical Under-Routing (M3 $\rightarrow$ M1)** | **4.67%** (7 / 150) |
| **Over-Routing Rate** | **6.00%** (9 / 150) |

---

## 2. 3x3 Confusion Matrix

| ACTUAL \ PREDICTED | PREDICTED M1 | PREDICTED M2 | PREDICTED M3 |
| :--- | :---: | :---: | :---: |
| **ACTUAL MODEL 1** | **38** | 6 | 1 |
| **ACTUAL MODEL 2** | 9 | **40** | 2 |
| **ACTUAL MODEL 3** | 7 | 4 | **43** |

---

## 3. Deterministic Latency Percentiles

| Percentile | Latency (ms) | Target |
| :--- | :---: | :---: |
| **Average Latency** | **0.311 ms** | < 10.0 ms |
| **Median (P50) Latency** | **0.265 ms** | < 10.0 ms |
| **P95 Latency** | **0.564 ms** | < 10.0 ms |
| **P99 Latency** | **1.064 ms** | < 10.0 ms |

---

## 4. Cost Reduction

- **Baseline ("Always Model 3")**: `$4.50` per 100 requests
- **Orchestrated Routing**: `$0.985` per 100 requests
- **Simulated Cost Savings**: **78.10% cost reduction**
