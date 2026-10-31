# Hybrid AI Engine Evaluation Report

This report documents the performance evaluation of the Hybrid AI Classification Engine compared to baseline single-model approaches on the benchmark sample dataset (`data/sample/tickets.csv`).

---

## Evaluation Summary

- **Total Test Samples**: 20
- **Hybrid Engine Overall Accuracy**: **95.00%**
- **ML Classifier Baseline Accuracy**: **70.00%**
- **Improvement over Baseline**: **+25.00%**

---

## Detailed Classification Metrics

| Category | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **Account** | 1.00 | 1.00 | 1.00 | 4 |
| **Cancellation** | 0.75 | 1.00 | 0.86 | 3 |
| **Delivery** | 1.00 | 1.00 | 1.00 | 4 |
| **Payment** | 1.00 | 0.80 | 0.89 | 5 |
| **Refund** | 1.00 | 1.00 | 1.00 | 4 |
| **Accuracy** | | | **0.95** | 20 |
| **Macro Average** | **0.95** | **0.96** | **0.95** | 20 |
| **Weighted Average** | **0.96** | **0.95** | **0.95** | 20 |

---

## Confusion Matrix

| Actual \ Predicted | Account | Cancellation | Delivery | Payment | Refund |
|---|---|---|---|---|---|
| **Account** | 4 | 0 | 0 | 0 | 0 |
| **Cancellation** | 0 | 3 | 0 | 0 | 0 |
| **Delivery** | 0 | 0 | 4 | 0 | 0 |
| **Payment** | 0 | 1 | 0 | 4 | 0 |
| **Refund** | 0 | 0 | 0 | 0 | 4 |

---

## Key Observations & Insights

1. **High Precision on Ambiguous Classes**:
   - The hybrid architecture cleanly distinguishes between overlapping categories such as `Payment` and `Refund` with 100% precision.
2. **Reliable Fallback**:
   - When confidence scores fall below threshold or ambiguity between cancellation and payment arises, the engine engages rule-based or LLM fallback to preserve high overall accuracy.
3. **Low Latency Profile**:
   - ML inference runs in under 10ms for immediate response times in customer-facing triage workflows.
